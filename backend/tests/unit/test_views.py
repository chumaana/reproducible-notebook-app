"""
Unit tests for Django views.
tests/unit/test_views.py
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from notebooks.models import Notebook, Execution, ReproducibilityAnalysis
from notebooks.views import NotebookViewSet, UserViewSet


class NotebookViewSetTest(TestCase):
    """Test NotebookViewSet methods"""

    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass"
        )
        self.notebook = Notebook.objects.create(
            title="Test Notebook", content="# Test", author=self.user
        )

    def test_get_queryset_filters_by_user(self):
        """Test queryset only returns notebooks for authenticated user"""
        other_user = User.objects.create_user(username="other", password="test")
        Notebook.objects.create(title="Other's Notebook", content="", author=other_user)

        view = NotebookViewSet.as_view({"get": "list"})
        request = self.factory.get("/api/notebooks/")
        force_authenticate(request, user=self.user)
        view.request = request

        response = view(request)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Notebook")

    def test_perform_create_assigns_author(self):
        """Test that author is auto-assigned on create"""
        view = NotebookViewSet.as_view({"post": "create"})
        data = {"title": "New Notebook", "content": "# Test"}

        request = self.factory.post("/api/notebooks/", data, format="json")
        force_authenticate(request, user=self.user)

        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        notebook = Notebook.objects.get(title="New Notebook")
        self.assertEqual(notebook.author, self.user)


class UserViewSetTest(TestCase):
    """Test UserViewSet methods"""

    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()

    def test_register_action(self):
        """Test user registration endpoint"""
        view = UserViewSet.as_view({"post": "register"})
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "ComplexPass123!",
        }

        request = self.factory.post("/api/users/register/", data)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_me_action(self):
        """Test current user profile endpoint"""
        user = User.objects.create_user(username="testuser", password="test")
        view = UserViewSet.as_view({"get": "me"})

        request = self.factory.get("/api/users/me/")
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")


class UserAuthViewsTest(TestCase):
    """Test authentication views"""

    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_user_register_view(self):
        """Test user registration view"""
        from notebooks.views import UserRegisterView

        view = UserRegisterView.as_view()
        data = {
            "username": "newuser_view",
            "email": "new_view@example.com",
            "password": "ComplexPass123!",
        }

        request = self.factory.post("/api/auth/register/", data)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)

    def test_user_login_view(self):
        """Test user login view"""
        from notebooks.views import UserLoginView

        view = UserLoginView.as_view()
        # Login doesn't validate complexity, just matches the DB.
        # So "testpass123" is fine here because setUp created it.
        data = {"username": "testuser", "password": "testpass123"}

        request = self.factory.post("/api/auth/login/", data)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_user_profile_view_get(self):
        """Test get user profile"""
        from notebooks.views import UserProfileView

        view = UserProfileView.as_view()
        request = self.factory.get("/api/auth/profile/")
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")

    def test_user_profile_view_patch(self):
        """Test update user profile"""
        from notebooks.views import UserProfileView

        view = UserProfileView.as_view()
        data = {"first_name": "Test", "last_name": "User"}

        request = self.factory.patch("/api/auth/profile/", data)
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Test")
        self.assertEqual(response.data["last_name"], "User")


class NotebookActionsTest(TestCase):
    """Test custom actions on NotebookViewSet"""

    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username="testuser", password="test")
        self.notebook = Notebook.objects.create(
            title="Test", content="```{r}\nprint('test')\n```", author=self.user
        )

    def test_download_action(self):
        """Test download .Rmd file action"""
        view = NotebookViewSet.as_view({"get": "download"})
        request = self.factory.get(f"/api/notebooks/{self.notebook.id}/download/")
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.notebook.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertIn("attachment", response["Content-Disposition"])

    def test_reproducibility_action_no_analysis(self):
        """Test reproducibility endpoint with no analysis"""
        view = NotebookViewSet.as_view({"get": "reproducibility"})
        request = self.factory.get(
            f"/api/notebooks/{self.notebook.id}/reproducibility/"
        )
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.notebook.id)

        # Should return 404 or empty response
        self.assertIn(
            response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]
        )

    def test_reproducibility_action_with_analysis(self):
        """Test reproducibility endpoint with analysis data"""
        analysis = ReproducibilityAnalysis.objects.create(
            notebook=self.notebook,
            dockerfile="FROM rocker/r-ver:4.3.0",
            dependencies=["ggplot2"],
        )

        view = NotebookViewSet.as_view({"get": "reproducibility"})
        request = self.factory.get(
            f"/api/notebooks/{self.notebook.id}/reproducibility/"
        )
        force_authenticate(request, user=self.user)

        response = view(request, pk=self.notebook.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("dockerfile", response.data)
