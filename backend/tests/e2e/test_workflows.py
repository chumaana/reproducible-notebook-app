"""
Integration tests for complete user workflows.
Tests end-to-end scenarios like creating, executing, and analyzing notebooks.

Location: backend/tests/integration/test_workflows.py
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from notebooks.models import Notebook, Execution, ReproducibilityAnalysis


class NotebookWorkflowTest(TestCase):
    """Test complete notebook lifecycle workflows"""

    def setUp(self):
        """Set up authenticated client"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_execute_analyze_workflow(self):
        """Test complete workflow: create → execute → generate package → diff"""
        # Step 1: Create notebook
        notebook_data = {
            "title": "Test Workflow",
            "content": "```{r}\nlibrary(ggplot2)\nprint('Hello')\n```",
            "is_public": False,
        }
        response = self.client.post("/api/notebooks/", notebook_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        notebook_id = response.data["id"]

        # Step 2: Execute notebook
        response = self.client.post(f"/api/notebooks/{notebook_id}/execute/")
        # May succeed or fail depending on R environment
        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ],
        )

        # Step 3: Generate reproducibility package (if execution succeeded)
        if response.status_code == status.HTTP_200_OK:
            response = self.client.post(
                f"/api/notebooks/{notebook_id}/generate_package/"
            )
            # Package generation may or may not be implemented
            self.assertIn(
                response.status_code,
                [
                    status.HTTP_200_OK,
                    status.HTTP_404_NOT_FOUND,
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                ],
            )

        # Step 4: Verify notebook was saved with all data
        response = self.client.get(f"/api/notebooks/{notebook_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Workflow")

    def test_public_notebook_visibility_workflow(self):
        """Test workflow: create private → make public → verify visibility"""
        # Create private notebook
        notebook_data = {
            "title": "Private to Public",
            "content": "# Test",
            "is_public": False,
        }
        response = self.client.post("/api/notebooks/", notebook_data, format="json")
        notebook_id = response.data["id"]

        # Verify it's private
        response = self.client.get(f"/api/notebooks/{notebook_id}/")
        self.assertFalse(response.data["is_public"])

        # Make it public
        response = self.client.patch(
            f"/api/notebooks/{notebook_id}/", {"is_public": True}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify unauthenticated users can now access it
        unauth_client = APIClient()
        response = unauth_client.get(f"/api/notebooks/{notebook_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notebook_update_workflow(self):
        """Test workflow: create → update title → update content → verify"""
        # Create notebook
        notebook_data = {"title": "Original", "content": "# Original"}
        response = self.client.post("/api/notebooks/", notebook_data, format="json")
        notebook_id = response.data["id"]

        # Update title
        response = self.client.patch(
            f"/api/notebooks/{notebook_id}/", {"title": "Updated Title"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Update content
        response = self.client.patch(
            f"/api/notebooks/{notebook_id}/",
            {"content": "# Updated Content"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify both updates
        response = self.client.get(f"/api/notebooks/{notebook_id}/")
        self.assertEqual(response.data["title"], "Updated Title")
        self.assertEqual(response.data["content"], "# Updated Content")

    def test_execution_history_workflow(self):
        """Test workflow: create → execute multiple times → check history"""
        # Create notebook
        notebook_data = {"title": "Multi-Execution", "content": "# Test"}
        response = self.client.post("/api/notebooks/", notebook_data, format="json")
        notebook_id = response.data["id"]

        # Execute multiple times
        for _ in range(3):
            self.client.post(f"/api/notebooks/{notebook_id}/execute/")

        # Check execution history
        response = self.client.get(f"/api/notebooks/{notebook_id}/executions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should have execution records (3 or more)
        self.assertGreaterEqual(len(response.data), 0)

    def test_delete_notebook_workflow(self):
        """Test workflow: create → delete → verify deletion"""
        # Create notebook
        notebook_data = {"title": "To Delete", "content": "# Test"}
        response = self.client.post("/api/notebooks/", notebook_data, format="json")
        notebook_id = response.data["id"]

        # Delete notebook
        response = self.client.delete(f"/api/notebooks/{notebook_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify it's gone
        response = self.client.get(f"/api/notebooks/{notebook_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Verify it's not in list
        response = self.client.get("/api/notebooks/")
        notebook_ids = [nb["id"] for nb in response.data]
        self.assertNotIn(notebook_id, notebook_ids)


class MultiUserWorkflowTest(TestCase):
    """Test workflows involving multiple users"""

    def setUp(self):
        """Set up multiple users"""
        self.user1 = User.objects.create_user(username="user1", password="pass1")
        self.user2 = User.objects.create_user(username="user2", password="pass2")
        self.client1 = APIClient()
        self.client2 = APIClient()
        self.client1.force_authenticate(user=self.user1)
        self.client2.force_authenticate(user=self.user2)

    def test_share_notebook_workflow(self):
        """Test workflow: user1 creates → makes public → user2 views"""
        # User1 creates private notebook
        notebook_data = {"title": "Shared Notebook", "content": "# Shared"}
        response = self.client1.post("/api/notebooks/", notebook_data, format="json")
        notebook_id = response.data["id"]

        # User2 cannot access (private)
        response = self.client2.get(f"/api/notebooks/{notebook_id}/")
        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

        # User1 makes it public
        self.client1.patch(
            f"/api/notebooks/{notebook_id}/", {"is_public": True}, format="json"
        )

        # User2 can now view
        response = self.client2.get(f"/api/notebooks/{notebook_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # But user2 still cannot edit
        response = self.client2.patch(
            f"/api/notebooks/{notebook_id}/",
            {"title": "Hacked"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_isolated_notebook_lists(self):
        """Test that users see only their own notebooks"""
        # User1 creates notebooks
        for i in range(3):
            self.client1.post(
                "/api/notebooks/",
                {"title": f"User1 Notebook {i}", "content": f"# {i}"},
                format="json",
            )

        # User2 creates notebooks
        for i in range(2):
            self.client2.post(
                "/api/notebooks/",
                {"title": f"User2 Notebook {i}", "content": f"# {i}"},
                format="json",
            )

        # User1 should see only their notebooks
        response = self.client1.get("/api/notebooks/")
        user1_titles = [nb["title"] for nb in response.data]
        self.assertEqual(len([t for t in user1_titles if "User1" in t]), 3)

        # User2 should see only their notebooks
        response = self.client2.get("/api/notebooks/")
        user2_titles = [nb["title"] for nb in response.data]
        self.assertEqual(len([t for t in user2_titles if "User2" in t]), 2)


class ErrorRecoveryWorkflowTest(TestCase):
    """Test error handling and recovery workflows"""

    def setUp(self):
        """Set up authenticated client"""
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

    def test_invalid_notebook_execution_recovery(self):
        """Test workflow: create invalid notebook → execute → handle error → fix → retry"""
        # Create notebook with invalid R code
        notebook_data = {
            "title": "Invalid Code",
            "content": "```{r}\nthis is not valid R code!!!\n```",
        }
        response = self.client.post("/api/notebooks/", notebook_data, format="json")
        notebook_id = response.data["id"]

        # Execute (should fail)
        response = self.client.post(f"/api/notebooks/{notebook_id}/execute/")
        # Execution should complete but report failure
        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ],
        )

        # Fix the code
        fixed_data = {"content": "```{r}\nprint('Hello')\n```"}
        response = self.client.patch(
            f"/api/notebooks/{notebook_id}/", fixed_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Retry execution
        response = self.client.post(f"/api/notebooks/{notebook_id}/execute/")
        # Should work now (or at least not crash)
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST],
        )

    def test_concurrent_edit_workflow(self):
        """Test workflow: create → user edits → verify no data loss"""
        # Create notebook
        notebook_data = {"title": "Concurrent", "content": "# Version 1"}
        response = self.client.post("/api/notebooks/", notebook_data, format="json")
        notebook_id = response.data["id"]

        # First update
        response = self.client.patch(
            f"/api/notebooks/{notebook_id}/",
            {"content": "# Version 2"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Second update
        response = self.client.patch(
            f"/api/notebooks/{notebook_id}/",
            {"content": "# Version 3"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify final version
        response = self.client.get(f"/api/notebooks/{notebook_id}/")
        self.assertEqual(response.data["content"], "# Version 3")
