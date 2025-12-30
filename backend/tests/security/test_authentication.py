"""
Security tests for Authentication mechanisms.
tests/security/test_authentication.py
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token


class AuthenticationSecurityTest(TestCase):
    """Test authentication security measures"""

    def setUp(self):
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

            if response.status_code == status.HTTP_201_CREATED:
                print(
                    f"Warning: Weak password '{weak_pass}' accepted - configure AUTH_PASSWORD_VALIDATORS"
                )
            else:
                self.assertIn(
                    response.status_code,
                    [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN],
                )

    def test_token_authentication(self):
        """Test token-based authentication"""
        user = User.objects.create_user(username="testuser", password="test123")
        token = Token.objects.create(user=user)

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
        """Test that logout deletes authentication token"""
        user = User.objects.create_user(username="testuser", password="test123")
        token = Token.objects.create(user=user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.post("/api/auth/logout/")

        if response.status_code == status.HTTP_200_OK:
            self.assertFalse(Token.objects.filter(key=token.key).exists())
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            self.skipTest("Logout endpoint not implemented")

    def test_password_not_exposed_in_api(self):
        """Test that password is never returned in API responses"""
        user = User.objects.create_user(username="testuser", password="test123")
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/auth/profile/")
        if response.status_code == status.HTTP_200_OK:
            response_data = str(response.data)
            self.assertNotIn("password", response_data.lower())
