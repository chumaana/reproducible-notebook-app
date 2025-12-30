"""
E2E Test: Multi-user Collaboration
tests/e2e/test_collaboration.py
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


class CollaborationWorkflowTest(TestCase):
    """Test workflows involving multiple users"""

    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass1")
        self.user2 = User.objects.create_user(username="user2", password="pass2")

        self.client1 = APIClient()
        self.client1.force_authenticate(user=self.user1)

        self.client2 = APIClient()
        self.client2.force_authenticate(user=self.user2)

    def test_share_notebook_workflow(self):
        """Test workflow: user1 creates -> makes public -> user2 views"""
        # 1. User1 creates PRIVATE notebook
        response = self.client1.post(
            "/api/notebooks/",
            {"title": "Shared NB", "content": "# Shared"},
            format="json",
        )
        notebook_id = response.data["id"]

        # 2. User2 tries to access (Should Fail)
        response = self.client2.get(f"/api/notebooks/{notebook_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # 3. User1 makes it PUBLIC
        self.client1.patch(
            f"/api/notebooks/{notebook_id}/", {"is_public": True}, format="json"
        )

        # 4. User2 reads (Should Succeed)
        response = self.client2.get(f"/api/notebooks/{notebook_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 5. User2 tries to edit (Should Fail - Read Only)
        response = self.client2.patch(
            f"/api/notebooks/{notebook_id}/", {"title": "Hacked"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_isolated_notebook_lists(self):
        """Test that users see only their own notebooks in the list view"""
        # User1 creates 2 notebooks
        self.client1.post(
            "/api/notebooks/", {"title": "U1-A", "content": "x"}, format="json"
        )
        self.client1.post(
            "/api/notebooks/", {"title": "U1-B", "content": "x"}, format="json"
        )

        # User2 creates 1 notebook
        self.client2.post(
            "/api/notebooks/", {"title": "U2-A", "content": "x"}, format="json"
        )

        # Verify User1 List
        response = self.client1.get("/api/notebooks/")
        titles1 = [nb["title"] for nb in response.data]
        self.assertIn("U1-A", titles1)
        self.assertNotIn("U2-A", titles1)

        # Verify User2 List
        response = self.client2.get("/api/notebooks/")
        titles2 = [nb["title"] for nb in response.data]
        self.assertIn("U2-A", titles2)
        self.assertNotIn("U1-A", titles2)
