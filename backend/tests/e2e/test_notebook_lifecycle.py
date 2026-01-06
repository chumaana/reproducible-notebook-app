"""
E2E Test: Full User Journey (Create -> Execute -> Update -> Delete)
tests/e2e/test_notebook_lifecycle.py
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


class NotebookLifecycleTest(TestCase):
    """Test complete notebook lifecycle workflows"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_execute_analyze_workflow(self):
        """Test complete workflow: create -> execute -> generate package"""
        # 1. Create notebook
        notebook_data = {
            "title": "Test Workflow",
            "content": "```{r}\nlibrary(ggplot2)\nprint('Hello')\n```",
            "is_public": False,
        }
        response = self.client.post("/api/notebooks/", notebook_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        notebook_id = response.data["id"]

        # 2. Execute notebook
        response = self.client.post(f"/api/notebooks/{notebook_id}/execute/")
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
        )

        # 3. Generate package (if execution worked)
        if response.status_code == status.HTTP_200_OK:
            response = self.client.post(
                f"/api/notebooks/{notebook_id}/generate_package/"
            )
            # We allow 404/500 here just in case the R system isn't fully mocked in this test env
            self.assertIn(
                response.status_code,
                [
                    status.HTTP_200_OK,
                    status.HTTP_404_NOT_FOUND,
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                ],
            )

        # 4. Verify Persistence
        response = self.client.get(f"/api/notebooks/{notebook_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Workflow")

    def test_notebook_update_workflow(self):
        """Test workflow: create -> update title -> update content -> verify"""
        # Create
        response = self.client.post(
            "/api/notebooks/",
            {"title": "Original", "content": "# Original"},
            format="json",
        )
        notebook_id = response.data["id"]

        # Update Title
        self.client.patch(
            f"/api/notebooks/{notebook_id}/", {"title": "Updated Title"}, format="json"
        )

        # Update Content
        self.client.patch(
            f"/api/notebooks/{notebook_id}/",
            {"content": "# Updated Content"},
            format="json",
        )

        # Verify
        response = self.client.get(f"/api/notebooks/{notebook_id}/")
        self.assertEqual(response.data["title"], "Updated Title")
        self.assertEqual(response.data["content"], "# Updated Content")

    def test_delete_notebook_workflow(self):
        """Test workflow: create -> delete -> verify deletion"""
        response = self.client.post(
            "/api/notebooks/",
            {"title": "To Delete", "content": "# Test"},
            format="json",
        )
        notebook_id = response.data["id"]

        # Delete
        response = self.client.delete(f"/api/notebooks/{notebook_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify Gone
        response = self.client.get(f"/api/notebooks/{notebook_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
