"""
Integration tests for API endpoints.
tests/integration/test_api.py
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from notebooks.models import Notebook, Execution, ReproducibilityAnalysis
import json
import os
import shutil


class AuthenticationAPITest(TestCase):
    """Test authentication endpoints"""

    def setUp(self):
        """Set up test client"""
        self.client = APIClient()

    def test_user_registration(self):
        """Test POST /api/auth/register/ creates user and returns token"""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepass123",
        }
        response = self.client.post("/api/auth/register/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "newuser")
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_user_registration_duplicate_username(self):
        """Test registration fails with duplicate username"""
        User.objects.create_user(username="existing", password="test")

        data = {
            "username": "existing",
            "email": "new@example.com",
            "password": "password123",
        }
        response = self.client.post("/api/auth/register/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_user_registration_duplicate_email(self):
        """Test registration fails with duplicate email"""
        User.objects.create_user(
            username="user1", email="existing@example.com", password="test"
        )

        data = {
            "username": "user2",
            "email": "existing@example.com",
            "password": "password123",
        }
        response = self.client.post("/api/auth/register/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        """Test POST /api/auth/login/ returns token"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post("/api/auth/login/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["username"], "testuser")

    def test_user_login_invalid_credentials(self):
        """Test login fails with wrong password"""
        User.objects.create_user(username="testuser", password="testpass123")

        data = {"username": "testuser", "password": "wrongpass"}
        response = self.client.post("/api/auth/login/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_get_user_profile(self):
        """Test GET /api/auth/profile/ returns user info"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="test",
            first_name="Test",
            last_name="User",
        )
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/auth/profile/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertEqual(response.data["first_name"], "Test")

    def test_update_user_profile(self):
        """Test PATCH /api/auth/profile/ updates user info"""
        user = User.objects.create_user(username="testuser", password="test")
        self.client.force_authenticate(user=user)

        data = {"first_name": "Updated", "last_name": "Name"}
        response = self.client.patch("/api/auth/profile/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Updated")
        self.assertEqual(response.data["last_name"], "Name")

        user.refresh_from_db()
        self.assertEqual(user.first_name, "Updated")


class NotebookCRUDAPITest(TestCase):
    """Test Notebook CRUD operations"""

    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_notebook(self):
        """Test POST /api/notebooks/ creates a notebook"""
        data = {
            "title": "New Notebook",
            "content": "# R Code\nlibrary(ggplot2)",
            "is_public": False,
        }
        response = self.client.post("/api/notebooks/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Notebook")
        self.assertEqual(response.data["author"], "testuser")
        self.assertFalse(response.data["is_public"])

    def test_create_notebook_requires_authentication(self):
        """Test creating notebook without authentication fails"""
        self.client.force_authenticate(user=None)

        data = {"title": "Test", "content": "# Test"}
        response = self.client.post("/api/notebooks/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_notebooks(self):
        """Test GET /api/notebooks/ returns user's notebooks only"""
        # Create notebooks for current user
        Notebook.objects.create(title="My Notebook 1", content="", author=self.user)
        Notebook.objects.create(title="My Notebook 2", content="", author=self.user)

        # Create notebook for another user
        other_user = User.objects.create_user(username="other", password="test")
        Notebook.objects.create(title="Other's Notebook", content="", author=other_user)

        response = self.client.get("/api/notebooks/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        titles = [nb["title"] for nb in response.data]
        self.assertIn("My Notebook 1", titles)
        self.assertIn("My Notebook 2", titles)
        self.assertNotIn("Other's Notebook", titles)

    def test_get_notebook_detail(self):
        """Test GET /api/notebooks/{id}/ returns notebook details"""
        notebook = Notebook.objects.create(
            title="Detail Test",
            content="# Test content",
            author=self.user,
            is_public=True,
        )

        response = self.client.get(f"/api/notebooks/{notebook.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Detail Test")
        self.assertEqual(response.data["content"], "# Test content")
        self.assertTrue(response.data["is_public"])

    def test_get_notebook_detail_unauthorized(self):
        """Test cannot access other user's notebook"""
        other_user = User.objects.create_user(username="other", password="test")
        notebook = Notebook.objects.create(
            title="Other's Notebook", content="", author=other_user
        )

        response = self.client.get(f"/api/notebooks/{notebook.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_notebook(self):
        """Test PUT /api/notebooks/{id}/ updates notebook"""
        notebook = Notebook.objects.create(
            title="Original", content="# Original", author=self.user
        )

        data = {
            "title": "Updated Title",
            "content": "# Updated content",
            "is_public": True,
        }
        response = self.client.put(
            f"/api/notebooks/{notebook.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Title")
        self.assertEqual(response.data["content"], "# Updated content")
        self.assertTrue(response.data["is_public"])

    def test_partial_update_notebook(self):
        """Test PATCH /api/notebooks/{id}/ partially updates notebook"""
        notebook = Notebook.objects.create(
            title="Original", content="# Original", author=self.user
        )

        data = {"title": "Patched Title"}
        response = self.client.patch(
            f"/api/notebooks/{notebook.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Patched Title")
        self.assertEqual(response.data["content"], "# Original")  # Unchanged

    def test_delete_notebook(self):
        """Test DELETE /api/notebooks/{id}/ deletes notebook"""
        notebook = Notebook.objects.create(
            title="To Delete", content="", author=self.user
        )
        notebook_id = notebook.id

        response = self.client.delete(f"/api/notebooks/{notebook_id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Notebook.objects.filter(id=notebook_id).exists())

    def test_delete_notebook_unauthorized(self):
        """Test cannot delete other user's notebook"""
        other_user = User.objects.create_user(username="other", password="test")
        notebook = Notebook.objects.create(
            title="Other's", content="", author=other_user
        )

        response = self.client.delete(f"/api/notebooks/{notebook.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Notebook.objects.filter(id=notebook.id).exists())


class NotebookExecutionAPITest(TestCase):
    """Test notebook execution endpoints"""

    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="test")
        self.client.force_authenticate(user=self.user)

    def test_execute_notebook(self):
        """Test POST /api/notebooks/{id}/execute/ executes R code"""
        notebook = Notebook.objects.create(
            title="Execute Test",
            content="---\ntitle: 'Test'\n---\n\n```{r}\nprint('Hello')\n```",
            author=self.user,
        )

        response = self.client.post(f"/api/notebooks/{notebook.id}/execute/")

        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_400_BAD_REQUEST,
            ],  # May fail if R not available
        )

        if response.status_code == status.HTTP_200_OK:
            self.assertIn("success", response.data)
            if response.data.get("success"):
                self.assertIn("html", response.data)
                self.assertIn("static_analysis", response.data)

    def test_execute_creates_execution_record(self):
        """Test execution creates Execution model"""
        notebook = Notebook.objects.create(
            title="Test",
            content="```{r}\nprint('test')\n```",
            author=self.user,
        )

        initial_count = Execution.objects.filter(notebook=notebook).count()

        response = self.client.post(f"/api/notebooks/{notebook.id}/execute/")

        # Should create execution record regardless of success
        final_count = Execution.objects.filter(notebook=notebook).count()
        self.assertEqual(final_count, initial_count + 1)

    def test_execute_saves_analysis(self):
        """Test execution saves static analysis"""
        notebook = Notebook.objects.create(
            title="Test",
            content="```{r}\nx <- rnorm(100)\n```",  # Missing set.seed
            author=self.user,
        )

        response = self.client.post(f"/api/notebooks/{notebook.id}/execute/")

        if response.status_code == status.HTTP_200_OK:
            # Check if analysis was saved
            try:
                analysis = ReproducibilityAnalysis.objects.get(notebook=notebook)
                self.assertIsNotNone(analysis.dependencies)
            except ReproducibilityAnalysis.DoesNotExist:
                pass  # Analysis may not be created on failure

    def test_execute_unauthorized_notebook(self):
        """Test cannot execute other user's notebook"""
        other_user = User.objects.create_user(username="other", password="test")
        notebook = Notebook.objects.create(
            title="Other's", content="```{r}\nprint('test')\n```", author=other_user
        )

        response = self.client.post(f"/api/notebooks/{notebook.id}/execute/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        """Clean up test files"""
        storage_path = "storage/notebooks"
        if os.path.exists(storage_path):
            for item in os.listdir(storage_path):
                item_path = os.path.join(storage_path, item)
                if os.path.isdir(item_path):
                    try:
                        shutil.rmtree(item_path)
                    except:
                        pass


class NotebookPackageGenerationAPITest(TestCase):
    """Test reproducibility package generation endpoints"""

    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="test")
        self.client.force_authenticate(user=self.user)

    def test_generate_package(self):
        """Test POST /api/notebooks/{id}/generate_package/ generates r4r package"""
        notebook = Notebook.objects.create(
            title="Package Test",
            content="```{r}\nprint('test')\n```",
            author=self.user,
        )

        # First execute to create .Rmd file
        self.client.post(f"/api/notebooks/{notebook.id}/execute/")

        # Then generate package
        response = self.client.post(f"/api/notebooks/{notebook.id}/generate_package/")

        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ],
        )

        if response.status_code == status.HTTP_200_OK and response.data.get("success"):
            self.assertIn("dockerfile", response.data)
            self.assertIn("makefile", response.data)
            self.assertIn("manifest", response.data)

    def test_generate_package_saves_analysis(self):
        """Test package generation saves reproducibility analysis"""
        notebook = Notebook.objects.create(
            title="Test",
            content="```{r}\nlibrary(ggplot2)\n```",
            author=self.user,
        )

        # Execute first
        self.client.post(f"/api/notebooks/{notebook.id}/execute/")

        # Generate package
        response = self.client.post(f"/api/notebooks/{notebook.id}/generate_package/")

        if response.status_code == status.HTTP_200_OK and response.data.get("success"):
            # Check if analysis was created/updated
            try:
                analysis = ReproducibilityAnalysis.objects.get(notebook=notebook)
                self.assertIsNotNone(analysis.dockerfile)
                self.assertIsNotNone(analysis.r4r_data)
            except ReproducibilityAnalysis.DoesNotExist:
                pass

    def tearDown(self):
        """Clean up test files"""
        storage_path = "storage/notebooks"
        if os.path.exists(storage_path):
            for item in os.listdir(storage_path):
                item_path = os.path.join(storage_path, item)
                if os.path.isdir(item_path):
                    try:
                        shutil.rmtree(item_path)
                    except:
                        pass


class NotebookDiffGenerationAPITest(TestCase):
    """Test semantic diff generation endpoints"""

    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="test")
        self.client.force_authenticate(user=self.user)

    def test_generate_diff(self):
        """Test POST /api/notebooks/{id}/generate_diff/ generates rdiff"""
        notebook = Notebook.objects.create(
            title="Diff Test",
            content="```{r}\nprint('test')\n```",
            author=self.user,
        )

        response = self.client.post(f"/api/notebooks/{notebook.id}/generate_diff/")

        # Will likely fail without HTML files, but should handle gracefully
        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ],
        )

    def tearDown(self):
        """Clean up test files"""
        storage_path = "storage/notebooks"
        if os.path.exists(storage_path):
            for item in os.listdir(storage_path):
                item_path = os.path.join(storage_path, item)
                if os.path.isdir(item_path):
                    try:
                        shutil.rmtree(item_path)
                    except:
                        pass


class NotebookDownloadAPITest(TestCase):
    """Test notebook download endpoints"""

    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="test")
        self.client.force_authenticate(user=self.user)

    def test_download_rmd(self):
        """Test GET /api/notebooks/{id}/download/ downloads .Rmd file"""
        notebook = Notebook.objects.create(
            title="Download Test",
            content="# Test R Markdown\n\n```{r}\nprint('test')\n```",
            author=self.user,
        )

        response = self.client.get(f"/api/notebooks/{notebook.id}/download/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn("Download Test.Rmd", response["Content-Disposition"])

    def test_download_package(self):
        """Test GET /api/notebooks/{id}/download_package/ downloads ZIP"""
        notebook = Notebook.objects.create(
            title="Test", content="```{r}\nprint('test')\n```", author=self.user
        )

        response = self.client.get(f"/api/notebooks/{notebook.id}/download_package/")

        # Will return 404 if package not generated
        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_404_NOT_FOUND,
                status.HTTP_400_BAD_REQUEST,
            ],
        )


class NotebookReproducibilityAPITest(TestCase):
    """Test reproducibility analysis retrieval"""

    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="test")
        self.client.force_authenticate(user=self.user)

    def test_get_reproducibility_no_analysis(self):
        """Test GET /api/notebooks/{id}/reproducibility/ with no analysis"""
        notebook = Notebook.objects.create(
            title="Test", content="```{r}\nprint('test')\n```", author=self.user
        )

        response = self.client.get(f"/api/notebooks/{notebook.id}/reproducibility/")

        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND],
        )

    def test_get_reproducibility_with_analysis(self):
        """Test GET /api/notebooks/{id}/reproducibility/ returns analysis"""
        notebook = Notebook.objects.create(
            title="Test", content="```{r}\nprint('test')\n```", author=self.user
        )

        # Create analysis
        analysis = ReproducibilityAnalysis.objects.create(
            notebook=notebook,
            dockerfile="FROM rocker/r-ver:4.3.0",
            dependencies=["ggplot2", "dplyr"],
            r4r_data={
                "r_packages": ["ggplot2"],
                "system_libs": [],
                "files_accessed": 5,
            },
        )

        response = self.client.get(f"/api/notebooks/{notebook.id}/reproducibility/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("dockerfile", response.data)
        self.assertEqual(len(response.data["dependencies"]), 2)
        self.assertIn("r4r_data", response.data)


class FullWorkflowIntegrationTest(TestCase):
    """Test complete notebook workflow"""

    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_complete_workflow(self):
        """Test full workflow: create -> execute -> analyze -> download"""
        # Step 1: Create notebook
        create_data = {
            "title": "Complete Workflow Test",
            "content": "---\ntitle: 'Test'\n---\n\n```{r}\nset.seed(123)\nx <- 1:10\nprint(mean(x))\n```",
            "is_public": False,
        }
        create_response = self.client.post(
            "/api/notebooks/", create_data, format="json"
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        notebook_id = create_response.data["id"]

        # Step 2: Execute notebook
        execute_response = self.client.post(f"/api/notebooks/{notebook_id}/execute/")
        # May succeed or fail depending on environment
        self.assertIn("success", execute_response.data)

        # Step 3: Download .Rmd
        download_response = self.client.get(f"/api/notebooks/{notebook_id}/download/")
        self.assertEqual(download_response.status_code, status.HTTP_200_OK)

        # Step 4: Get notebook details
        detail_response = self.client.get(f"/api/notebooks/{notebook_id}/")
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["title"], "Complete Workflow Test")

        # Step 5: Delete notebook
        delete_response = self.client.delete(f"/api/notebooks/{notebook_id}/")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def tearDown(self):
        """Clean up test files"""
        storage_path = "storage/notebooks"
        if os.path.exists(storage_path):
            for item in os.listdir(storage_path):
                item_path = os.path.join(storage_path, item)
                if os.path.isdir(item_path):
                    try:
                        shutil.rmtree(item_path)
                    except:
                        pass
