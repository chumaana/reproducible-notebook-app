"""
Integration tests for API Data Contracts.
tests/integration/test_api_contracts.py
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from notebooks.models import Notebook


class APIContractTest(TestCase):
    """Test JSON response structures and data types matches Serializers"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="contract_user", password="password"
        )
        self.client.force_authenticate(user=self.user)

        self.notebook = Notebook.objects.create(
            title="Schema Test", content="# Content", author=self.user, is_public=False
        )

    def test_notebook_detail_structure(self):
        """
        Verify the notebook detail endpoint returns the exact keys
        defined in NotebookSerializer.
        """
        response = self.client.get(f"/api/notebooks/{self.notebook.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        # 1. Define expected keys based on NotebookSerializer fields
        expected_keys = {
            "id",
            "title",
            "author",  # ReadOnlyField(source='author.username')
            "author_id",  # ReadOnlyField(source='author.id')
            "content",
            "created_at",
            "updated_at",
            "is_public",
            "analysis",  # Nested Serializer
            "execution_count",  # SerializerMethodField
            "last_execution_status",  # SerializerMethodField
            "has_analysis",  # SerializerMethodField
        }

        # 2. Check strict key existence
        self.assertTrue(
            expected_keys.issubset(data.keys()),
            f"Response missing keys: {expected_keys - set(data.keys())}",
        )

        # 3. Check Data Types
        self.assertIsInstance(data["id"], int)
        self.assertIsInstance(data["title"], str)
        self.assertIsInstance(data["is_public"], bool)
        self.assertIsInstance(data["execution_count"], int)

        # 4. specific check for author fields based on your serializer
        self.assertIsInstance(data["author"], str)  # Should be "contract_user"
        self.assertEqual(data["author"], "contract_user")
        self.assertIsInstance(data["author_id"], int)

    def test_notebook_list_structure(self):
        """Verify list endpoint return structure"""
        response = self.client.get("/api/notebooks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Handle DRF Pagination (List vs Dict with 'results')
        if isinstance(response.data, dict) and "results" in response.data:
            results = response.data["results"]
        else:
            results = response.data

        self.assertIsInstance(results, list)
        if results:
            item = results[0]
            self.assertIn("title", item)
            self.assertIn("author", item)
            self.assertIn("has_analysis", item)

    def test_json_content_type_header(self):
        """Ensure the server declares the response as JSON"""
        response = self.client.get("/api/notebooks/")
        self.assertTrue("application/json" in response["Content-Type"])
