"""
Integration tests for Public/Private Notebook sharing logic.
tests/integration/test_public_notebooks.py
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from notebooks.models import Notebook


class PublicNotebookFeatureTest(TestCase):
    """Test notebook sharing permissions and visibility controls."""

    def setUp(self):
        self.client = APIClient()

        self.owner = User.objects.create_user(username="owner", password="password")
        self.viewer = User.objects.create_user(username="viewer", password="password")

        self.public_nb = Notebook.objects.create(
            title="Public NB",
            content="Everyone can see this",
            author=self.owner,
            is_public=True,
        )

        self.private_nb = Notebook.objects.create(
            title="Private NB",
            content="Only I can see this",
            author=self.owner,
            is_public=False,
        )

    def test_viewer_can_read_public_notebook(self):
        """Authenticated non-owners can view public notebooks."""
        self.client.force_authenticate(user=self.viewer)

        response = self.client.get(f"/api/notebooks/{self.public_nb.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Public NB")

    def test_viewer_cannot_read_private_notebook(self):
        """
        Non-owners cannot view private notebooks.

        Returns 404 because get_queryset filters by (owner OR public),
        so private notebooks owned by others are not in the queryset.
        """
        self.client.force_authenticate(user=self.viewer)

        response = self.client.get(f"/api/notebooks/{self.private_nb.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_viewer_cannot_edit_public_notebook(self):
        """
        Public notebooks are read-only for non-owners.

        IsOwnerOrReadOnlyIfPublic permission allows reads but blocks writes
        for authenticated users who are not the owner.
        """
        self.client.force_authenticate(user=self.viewer)

        data = {"title": "Hacked Title"}
        response = self.client.patch(f"/api/notebooks/{self.public_nb.id}/", data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.public_nb.refresh_from_db()
        self.assertEqual(self.public_nb.title, "Public NB")

    def test_anonymous_user_can_read_public_notebook(self):
        """
        Unauthenticated users can read public notebooks.

        get_permissions returns AllowAny for 'retrieve' action.
        """
        self.client.logout()

        response = self.client.get(f"/api/notebooks/{self.public_nb.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_toggle_public_action(self):
        """
        Owner can toggle notebook visibility via toggle_public endpoint.

        Tests:
        - Private to public transition
        - Database persistence
        - Public to private transition
        """
        self.client.force_authenticate(user=self.owner)

        self.assertFalse(self.private_nb.is_public)

        response = self.client.post(
            f"/api/notebooks/{self.private_nb.id}/toggle_public/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_public"])
        self.assertIn("message", response.data)

        self.private_nb.refresh_from_db()
        self.assertTrue(self.private_nb.is_public)

        response = self.client.post(
            f"/api/notebooks/{self.private_nb.id}/toggle_public/"
        )
        self.assertFalse(response.data["is_public"])

    def test_non_owner_cannot_toggle_public(self):
        """Non-owners cannot change notebook visibility settings."""
        self.client.force_authenticate(user=self.viewer)

        response = self.client.post(
            f"/api/notebooks/{self.public_nb.id}/toggle_public/"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
