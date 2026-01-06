"""
Security tests for Authorization and Access Control.
tests/security/test_authorization.py
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from notebooks.models import Notebook, Execution


class AuthorizationSecurityTest(TestCase):
    """Test authorization rules"""

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="user1", password="test123")
        self.user2 = User.objects.create_user(username="user2", password="test123")
        self.notebook1 = Notebook.objects.create(
            title="User1 Notebook", content="# Content", author=self.user1
        )

    def test_user_cannot_access_other_notebooks(self):
        """Test that users cannot access notebooks they don't own"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f"/api/notebooks/{self.notebook1.id}/")

        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

    def test_user_cannot_update_other_notebooks(self):
        """Test that users cannot update notebooks they don't own"""
        self.client.force_authenticate(user=self.user2)
        data = {"title": "Hacked Title", "content": "# Hacked"}
        response = self.client.put(f"/api/notebooks/{self.notebook1.id}/", data)

        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

        self.notebook1.refresh_from_db()
        self.assertEqual(self.notebook1.title, "User1 Notebook")

    def test_public_notebook_access(self):
        """Test public notebook access"""
        public_notebook = Notebook.objects.create(
            title="Public Notebook",
            content="# Public",
            author=self.user1,
            is_public=True,
        )

        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f"/api/notebooks/{public_notebook.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cannot_create_notebook(self):
        """Test that unauthenticated users cannot create notebooks"""
        data = {"title": "Unauthorized", "content": "# Test"}
        response = self.client.post("/api/notebooks/", data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_only_sees_own_notebooks(self):
        """Test that users only see their own notebooks in list"""
        Notebook.objects.create(
            title="User2 Notebook", content="# Test", author=self.user2
        )

        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/api/notebooks/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [nb["title"] for nb in response.data]
        self.assertIn("User1 Notebook", titles)
        # User 2's private notebook should NOT be here
        self.assertNotIn("User2 Notebook", titles)


class DataIsolationTest(TestCase):
    """Test that execution and analysis data is isolated"""

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="user1", password="test123")
        self.user2 = User.objects.create_user(username="user2", password="test123")

    def test_notebook_execution_isolation(self):
        """Test that execution results are isolated between users"""
        notebook1 = Notebook.objects.create(
            title="User1 NB", content="# Test", author=self.user1
        )
        Execution.objects.create(
            notebook=notebook1, status="completed", html_output="<html>Private</html>"
        )

        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f"/api/notebooks/{notebook1.id}/executions/")

        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

    def test_reproducibility_analysis_isolation(self):
        """Test that analysis data is isolated between users"""
        notebook1 = Notebook.objects.create(
            title="User1 NB", content="# Test", author=self.user1
        )

        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f"/api/notebooks/{notebook1.id}/reproducibility/")

        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )
