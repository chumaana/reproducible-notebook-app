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
    """Test logic specific to the Sharing Feature"""

    def setUp(self):
        self.client = APIClient()

        # User 1: The Owner
        self.owner = User.objects.create_user(username="owner", password="password")

        # User 2: The Viewer (Authenticated but not owner)
        self.viewer = User.objects.create_user(username="viewer", password="password")

        # Public Notebook
        self.public_nb = Notebook.objects.create(
            title="Public NB",
            content="Everyone can see this",
            author=self.owner,
            is_public=True,
        )

        # Private Notebook
        self.private_nb = Notebook.objects.create(
            title="Private NB",
            content="Only I can see this",
            author=self.owner,
            is_public=False,
        )

    def test_viewer_can_read_public_notebook(self):
        """Feature: Authenticated non-owners can view public notebooks"""
        self.client.force_authenticate(user=self.viewer)

        response = self.client.get(f"/api/notebooks/{self.public_nb.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Public NB")

    def test_viewer_cannot_read_private_notebook(self):
        """
        Feature: Users cannot view private notebooks they don't own.
        Because your `get_queryset` filters by user|public,
        accessing a private ID owned by someone else results in 404 (Not Found).
        """
        self.client.force_authenticate(user=self.viewer)

        response = self.client.get(f"/api/notebooks/{self.private_nb.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_viewer_cannot_edit_public_notebook(self):
        """Feature: Public access is Read-Only for non-owners (IsOwnerOrReadOnlyIfPublic)"""
        self.client.force_authenticate(user=self.viewer)

        # Try to change the title
        data = {"title": "Hacked Title"}
        response = self.client.patch(f"/api/notebooks/{self.public_nb.id}/", data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify DB is unchanged
        self.public_nb.refresh_from_db()
        self.assertEqual(self.public_nb.title, "Public NB")

    def test_anonymous_user_can_read_public_notebook(self):
        """
        Feature: Unauthenticated users can read public notebooks.
        (Your get_permissions allows AllowAny for 'retrieve')
        """
        self.client.logout()

        response = self.client.get(f"/api/notebooks/{self.public_nb.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_toggle_public_action(self):
        """
        Feature: Owner can toggle status via the specific action endpoint.
        Endpoint: POST /api/notebooks/{id}/toggle_public/
        """
        self.client.force_authenticate(user=self.owner)

        # 1. Start Private
        self.assertFalse(self.private_nb.is_public)

        # 2. Call the action (POST)
        response = self.client.post(
            f"/api/notebooks/{self.private_nb.id}/toggle_public/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_public"])
        self.assertIn("message", response.data)

        # 3. Verify DB update
        self.private_nb.refresh_from_db()
        self.assertTrue(self.private_nb.is_public)

        # 4. Toggle back
        response = self.client.post(
            f"/api/notebooks/{self.private_nb.id}/toggle_public/"
        )
        self.assertFalse(response.data["is_public"])

    def test_non_owner_cannot_toggle_public(self):
        """Feature: Viewers cannot toggle visibility"""
        self.client.force_authenticate(user=self.viewer)

        response = self.client.post(
            f"/api/notebooks/{self.public_nb.id}/toggle_public/"
        )

        # Your view explicitly checks: if notebook.author != request.user -> 403
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
