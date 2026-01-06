"""
E2E Test: Error Handling and Recovery
tests/e2e/test_error_recovery.py
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


class ErrorRecoveryWorkflowTest(TestCase):
    """Test error handling and recovery workflows"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

    def test_invalid_notebook_execution_recovery(self):
        """Test workflow: create invalid notebook -> execute -> handle error -> fix -> retry"""
        # 1. Create invalid code
        notebook_data = {
            "title": "Invalid Code",
            "content": "```{r}\nINVALID_SYNTAX!!!\n```",
        }
        response = self.client.post("/api/notebooks/", notebook_data, format="json")
        notebook_id = response.data["id"]

        # 2. Execute (Should handle failure gracefully)
        response = self.client.post(f"/api/notebooks/{notebook_id}/execute/")

        # We expect a 200/400 (application handled it), definitely not 500 (crash)
        self.assertNotEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 3. Fix the code
        fixed_data = {"content": "```{r}\nprint('Fixed')\n```"}
        self.client.patch(f"/api/notebooks/{notebook_id}/", fixed_data, format="json")

        # 4. Retry execution
        response = self.client.post(f"/api/notebooks/{notebook_id}/execute/")
        # Should be successful now
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED]
        )

    def test_concurrent_edit_workflow(self):
        """Test workflow: sequential edits do not cause data loss"""
        # Create
        response = self.client.post(
            "/api/notebooks/", {"title": "Concurrent", "content": "v1"}, format="json"
        )
        notebook_id = response.data["id"]

        # Update 1
        self.client.patch(
            f"/api/notebooks/{notebook_id}/", {"content": "v2"}, format="json"
        )

        # Update 2
        self.client.patch(
            f"/api/notebooks/{notebook_id}/", {"content": "v3"}, format="json"
        )

        # Verify final state is v3
        response = self.client.get(f"/api/notebooks/{notebook_id}/")
        self.assertEqual(response.data["content"], "v3")
