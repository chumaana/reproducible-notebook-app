"""
Smoke Test: Critical Path Health Check.
Verifies the system is alive and core functionality works.
tests/smoke/test_critical_paths.py
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


class SystemHealthCheck(TestCase):
    """
    Fast validation that the application handles requests.
    Run this before full integration suites.
    """

    def setUp(self):
        self.client = APIClient()

    def test_api_root_reachable(self):
        """Check if the API root endpoint responds"""
        # Assuming you have a root view, or at least the server is up
        # If you don't have a root '/', try '/api/' or a known public endpoint
        try:
            response = self.client.get("/api/")
            # 200, 401, 403 are all signs the server is "alive" (not 500 or Connection Refused)
            self.assertNotEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            self.fail(f"System is unreachable: {e}")

    def test_database_write_check(self):
        """Check if the database is writable (Create User)"""
        try:
            user = User.objects.create_user(username="smoke_test", password="password")
            self.assertTrue(User.objects.filter(username="smoke_test").exists())
        except Exception as e:
            self.fail(f"Database write failed: {e}")

    def test_core_notebook_creation(self):
        """Check critical path: Login -> Create Notebook"""
        # 1. Register/Create User
        user = User.objects.create_user(username="smoke_user", password="password")
        self.client.force_authenticate(user=user)

        # 2. Create Notebook
        data = {"title": "Smoke Test NB", "content": "# content"}
        response = self.client.post("/api/notebooks/", data)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Critical Failure: Cannot create notebooks",
        )
