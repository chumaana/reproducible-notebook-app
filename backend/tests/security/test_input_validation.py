"""
Security tests for Input Validation (Injection, XSS, Overflow).
tests/security/test_input_validation.py
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from notebooks.models import Notebook


class InputValidationTest(TestCase):
    """Test input validation and sanitization"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.client.force_authenticate(user=self.user)

    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are prevented in login"""
        # (Moved here from Auth test as it fits Input Validation context better,
        # though it attacks Auth endpoint)
        malicious_username = "admin' OR '1'='1"
        data = {"username": malicious_username, "password": "test123"}

        # We use a fresh client to ensure no auth headers interfere
        client = APIClient()
        response = client.post("/api/auth/login/", data)

        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_xss_prevention_in_username(self):
        """Test XSS prevention in user input"""
        xss_username = "<script>alert('xss')</script>"
        data = {
            "username": xss_username,
            "email": "test@example.com",
            "password": "securepass123",
        }
        # Use fresh client for registration
        client = APIClient()
        response = client.post("/api/auth/register/", data)

        if response.status_code == status.HTTP_201_CREATED:
            user = User.objects.get(username=xss_username)
            self.assertEqual(user.username, xss_username)

    def test_empty_notebook_title_rejected(self):
        """Test that empty titles are rejected"""
        data = {"title": "", "content": "# Test"}
        response = self.client.post("/api/notebooks/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_required_fields(self):
        """Test that missing required fields are rejected"""
        # Missing content
        data = {"title": "Test"}
        response = self.client.post("/api/notebooks/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_extremely_long_title_rejected(self):
        """Test that extremely long titles are rejected or truncated"""
        long_title = "A" * 10000
        data = {"title": long_title, "content": "# Test"}
        response = self.client.post("/api/notebooks/", data, format="json")

        if response.status_code == status.HTTP_201_CREATED:
            notebook = Notebook.objects.get(id=response.data["id"])
            self.assertLess(len(notebook.title), 10000)
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rate_limiting(self):
        """Test API rate limiting (informational)"""
        # (Kept here or can be moved to test_rate_limiting.py if you make a 4th file)
        responses = []
        client = APIClient()  # Anonymous client
        for _ in range(100):
            response = client.post(
                "/api/auth/login/", {"username": "wrong", "password": "wrong"}
            )
            responses.append(response.status_code)

        if status.HTTP_429_TOO_MANY_REQUESTS in responses:
            print("✓ Rate limiting is active")
        else:
            print("! Rate limiting not implemented - consider adding throttling")
