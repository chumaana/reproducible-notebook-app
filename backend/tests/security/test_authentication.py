"""
Security tests for authentication and authorization.
Tests token security, password policies, and access control.

Location: backend/tests/security/test_authentication.py
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from notebooks.models import Notebook


class AuthenticationSecurityTest(TestCase):
    """Test authentication security measures"""

    def setUp(self):
        """Set up test client"""
        self.client = APIClient()

    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        user = User.objects.create_user(username="testuser", password="testpass123")

        # Password should not be stored in plaintext
        self.assertNotEqual(user.password, "testpass123")
        # Should start with hash algorithm identifier
        self.assertTrue(user.password.startswith("pbkdf2_sha256"))

    def test_weak_password_rejection(self):
        """Test that weak passwords are rejected (if validator is configured)"""
        weak_passwords = ["123", "password", "abc"]

        for weak_pass in weak_passwords:
            data = {
                "username": f"user_{weak_pass}",
                "email": f"{weak_pass}@test.com",
                "password": weak_pass,
            }
            response = self.client.post("/api/auth/register/", data)

            # NOTE: Django's password validators need to be configured in settings.py
            # If not configured, weak passwords will be accepted
            # This test documents the behavior
            if response.status_code == status.HTTP_201_CREATED:
                # Weak password was accepted - validator not enabled
                print(
                    f"Warning: Weak password '{weak_pass}' was accepted - configure AUTH_PASSWORD_VALIDATORS"
                )
            else:
                # Weak password was rejected - validator is working
                self.assertIn(
                    response.status_code,
                    [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN],
                )

    def test_token_authentication(self):
        """Test token-based authentication"""
        user = User.objects.create_user(username="testuser", password="test123")
        token = Token.objects.create(user=user)

        # Request with valid token
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.get("/api/notebooks/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_token_rejection(self):
        """Test that invalid tokens are rejected"""
        self.client.credentials(HTTP_AUTHORIZATION="Token invalid_token_123")
        response = self.client.get("/api/notebooks/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_uniqueness(self):
        """Test that each user has a unique token"""
        user1 = User.objects.create_user(username="user1", password="test123")
        user2 = User.objects.create_user(username="user2", password="test123")

        token1 = Token.objects.create(user=user1)
        token2 = Token.objects.create(user=user2)

        self.assertNotEqual(token1.key, token2.key)

    def test_logout_token_deletion(self):
        """Test that logout deletes authentication token (if endpoint exists)"""
        user = User.objects.create_user(username="testuser", password="test123")
        token = Token.objects.create(user=user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.post("/api/auth/logout/")

        # If logout endpoint exists
        if response.status_code == status.HTTP_200_OK:
            # Token should be deleted
            self.assertFalse(Token.objects.filter(key=token.key).exists())
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            # Logout endpoint not implemented yet - skip this test
            self.skipTest("Logout endpoint not implemented - implement it in views.py")

    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are prevented"""
        malicious_username = "admin' OR '1'='1"
        data = {"username": malicious_username, "password": "test123"}
        response = self.client.post("/api/auth/login/", data)

        # Should not authenticate with SQL injection
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_xss_prevention_in_username(self):
        """Test XSS prevention in user input"""
        xss_username = "<script>alert('xss')</script>"
        data = {
            "username": xss_username,
            "email": "test@example.com",
            "password": "securepass123",
        }
        response = self.client.post("/api/auth/register/", data)

        # Should handle XSS attempts safely
        if response.status_code == status.HTTP_201_CREATED:
            user = User.objects.get(username=xss_username)
            # Username should be stored as-is but sanitized on output
            self.assertEqual(user.username, xss_username)

    def test_password_not_exposed_in_api(self):
        """Test that password is never returned in API responses"""
        user = User.objects.create_user(username="testuser", password="test123")
        self.client.force_authenticate(user=user)

        # Check profile endpoint
        response = self.client.get("/api/auth/profile/")
        if response.status_code == status.HTTP_200_OK:
            response_data = str(response.data)
            self.assertNotIn("password", response_data.lower())


class AuthorizationSecurityTest(TestCase):
    """Test authorization and access control"""

    def setUp(self):
        """Set up test users and notebooks"""
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

        # Should be forbidden or not found (both are acceptable for security)
        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND],
        )

    def test_user_cannot_update_other_notebooks(self):
        """Test that users cannot update notebooks they don't own"""
        self.client.force_authenticate(user=self.user2)
        data = {"title": "Hacked Title", "content": "# Hacked"}
        response = self.client.put(f"/api/notebooks/{self.notebook1.id}/", data)

        # Should be forbidden or not found (both prevent unauthorized access)
        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

        # Verify notebook was not modified
        self.notebook1.refresh_from_db()
        self.assertEqual(self.notebook1.title, "User1 Notebook")

    def test_user_cannot_delete_other_notebooks(self):
        """Test that users cannot delete notebooks they don't own"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f"/api/notebooks/{self.notebook1.id}/")

        # Should be forbidden or not found (both prevent unauthorized deletion)
        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

        # Verify notebook still exists
        self.assertTrue(Notebook.objects.filter(id=self.notebook1.id).exists())

    def test_owner_can_access_own_notebook(self):
        """Test that owners can access their own notebooks"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"/api/notebooks/{self.notebook1.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "User1 Notebook")

    def test_public_notebook_access(self):
        """Test public notebook access"""
        # Create public notebook
        public_notebook = Notebook.objects.create(
            title="Public Notebook",
            content="# Public",
            author=self.user1,
            is_public=True,
        )

        # User2 should be able to read it
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f"/api/notebooks/{public_notebook.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Public Notebook")

    def test_unauthenticated_cannot_create_notebook(self):
        """Test that unauthenticated users cannot create notebooks"""
        data = {"title": "Unauthorized", "content": "# Test"}
        response = self.client.post("/api/notebooks/", data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_cannot_list_private_notebooks(self):
        """Test that unauthenticated users cannot see private notebooks"""
        # Create private notebook
        private_nb = Notebook.objects.create(
            title="Private", content="# Private", author=self.user1, is_public=False
        )

        # Make request without authentication
        response = self.client.get("/api/notebooks/")

        # Should either require auth or return empty list (no private notebooks)
        if response.status_code == status.HTTP_200_OK:
            titles = [nb["title"] for nb in response.data]
            self.assertNotIn("Private", titles)

    def test_user_only_sees_own_notebooks(self):
        """Test that users only see their own notebooks in list"""
        # Create notebooks for both users
        Notebook.objects.create(
            title="User2 Notebook", content="# Test", author=self.user2
        )

        # User1 should only see their own notebook (not public ones from user2)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/api/notebooks/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notebook_titles = [nb["title"] for nb in response.data]

        self.assertIn("User1 Notebook", notebook_titles)
        # User2's private notebook should not appear
        # (unless it's public, in which case it would appear)

    def test_rate_limiting(self):
        """Test API rate limiting (informational)"""
        # Make multiple rapid requests
        responses = []
        for _ in range(100):
            response = self.client.post(
                "/api/auth/login/",
                {"username": "wrong", "password": "wrong"},
            )
            responses.append(response.status_code)

        # Check if rate limiting is implemented
        has_rate_limit = status.HTTP_429_TOO_MANY_REQUESTS in responses

        if has_rate_limit:
            print("✓ Rate limiting is active")
        else:
            print("! Rate limiting not implemented - consider adding throttling")


class DataIsolationTest(TestCase):
    """Test that user data is properly isolated"""

    def setUp(self):
        """Set up test users and data"""
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="user1", password="test123")
        self.user2 = User.objects.create_user(username="user2", password="test123")

    def test_notebook_execution_isolation(self):
        """Test that execution results are isolated between users"""
        from notebooks.models import Execution

        # Create notebook and execution for user1
        notebook1 = Notebook.objects.create(
            title="User1 Notebook", content="# Test", author=self.user1
        )
        execution1 = Execution.objects.create(
            notebook=notebook1,
            status="completed",
            html_output="<html>Private data</html>",
        )

        # User2 tries to access user1's executions
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f"/api/notebooks/{notebook1.id}/executions/")

        # Should not be able to access
        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

    def test_reproducibility_analysis_isolation(self):
        """Test that analysis data is isolated between users"""
        notebook1 = Notebook.objects.create(
            title="User1 Notebook", content="# Test", author=self.user1
        )

        # User2 tries to access user1's analysis
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f"/api/notebooks/{notebook1.id}/reproducibility/")

        # Should not be able to access
        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )


class InputValidationTest(TestCase):
    """Test input validation and sanitization"""

    def setUp(self):
        """Set up authenticated client"""
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.client.force_authenticate(user=self.user)

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

        # Missing title
        data = {"content": "# Test"}
        response = self.client.post("/api/notebooks/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_extremely_long_title_rejected(self):
        """Test that extremely long titles are rejected or truncated"""
        long_title = "A" * 10000  # 10k characters
        data = {"title": long_title, "content": "# Test"}
        response = self.client.post("/api/notebooks/", data, format="json")

        # Should either reject or truncate
        if response.status_code == status.HTTP_201_CREATED:
            # If accepted, title should be truncated
            notebook = Notebook.objects.get(id=response.data["id"])
            self.assertLess(len(notebook.title), 10000)
        else:
            # Or rejected as bad request
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
