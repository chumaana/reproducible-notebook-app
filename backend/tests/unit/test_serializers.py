"""
Unit tests for Django REST Framework serializers.
Tests serialization/deserialization of notebook models.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from notebooks.models import Notebook, Execution, ReproducibilityAnalysis
from notebooks.serializers import (
    NotebookSerializer,
    ExecutionSerializer,
    ReproducibilityAnalysisSerializer,
    UserSerializer,
)
from django.utils import timezone


class NotebookSerializerTest(TestCase):
    """Test NotebookSerializer"""

    def setUp(self):
        """Set up test user and notebook"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass"
        )
        self.notebook_data = {
            "title": "Test Notebook",
            "content": "# R Script\nlibrary(ggplot2)",
            "is_public": False,
        }

    def test_serialize_notebook(self):
        """Test notebook serialization"""
        notebook = Notebook.objects.create(author=self.user, **self.notebook_data)
        serializer = NotebookSerializer(notebook)
        data = serializer.data

        self.assertEqual(data["title"], "Test Notebook")
        self.assertEqual(data["author"], "testuser")
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_deserialize_notebook(self):
        """Test notebook deserialization"""
        serializer = NotebookSerializer(data=self.notebook_data)
        self.assertTrue(serializer.is_valid())

        notebook = serializer.save(author=self.user)
        self.assertEqual(notebook.title, "Test Notebook")
        self.assertEqual(notebook.author, self.user)

    def test_notebook_validation_missing_title(self):
        """Test validation fails when title is missing"""
        invalid_data = {"content": "# Test"}
        serializer = NotebookSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_notebook_validation_empty_content(self):
        """Test validation rejects empty content"""
        data = {"title": "Empty Notebook", "content": ""}
        serializer = NotebookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_notebook_validation_whitespace_content(self):
        """Test validation rejects whitespace-only content"""
        data = {"title": "Whitespace Notebook", "content": "   \n\n   "}
        serializer = NotebookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_notebook_update(self):
        """Test notebook update via serializer"""
        notebook = Notebook.objects.create(author=self.user, **self.notebook_data)
        update_data = {"title": "Updated Title", "content": "# Updated"}

        serializer = NotebookSerializer(notebook, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()

        self.assertEqual(updated.title, "Updated Title")
        self.assertEqual(updated.content, "# Updated")


class ExecutionSerializerTest(TestCase):
    """Test ExecutionSerializer"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username="testuser", password="test")
        self.notebook = Notebook.objects.create(
            title="Test", content="# Test", author=self.user
        )

    def test_serialize_execution(self):
        """Test execution serialization"""
        execution = Execution.objects.create(
            notebook=self.notebook,
            status="completed",
            html_output="<html>Output</html>",
        )
        serializer = ExecutionSerializer(execution)
        data = serializer.data

        self.assertEqual(data["status"], "completed")
        self.assertIn("started_at", data)
        self.assertIn("html_output", data)

    def test_execution_status_choices(self):
        """Test execution status validation"""
        invalid_data = {
            "notebook": self.notebook.id,
            "status": "invalid_status",
        }
        serializer = ExecutionSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_execution_duration_field(self):
        """Test duration field is included in serialization"""
        execution = Execution.objects.create(
            notebook=self.notebook,
            status="completed",
            html_output="<html></html>",
        )
        execution.completed_at = execution.started_at + timezone.timedelta(seconds=5)
        execution.save()

        serializer = ExecutionSerializer(execution)
        self.assertIn("duration_seconds", serializer.data)


class ReproducibilityAnalysisSerializerTest(TestCase):
    """Test ReproducibilityAnalysisSerializer"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username="testuser", password="test")
        self.notebook = Notebook.objects.create(
            title="Analysis Test", content="# Test", author=self.user
        )

    def test_serialize_analysis(self):
        """Test analysis serialization"""
        analysis = ReproducibilityAnalysis.objects.create(
            notebook=self.notebook,
            dockerfile="FROM rocker/r-ver:4.3.0",
            dependencies=["ggplot2", "dplyr"],
        )
        serializer = ReproducibilityAnalysisSerializer(analysis)
        data = serializer.data

        self.assertIn("dockerfile", data)
        self.assertEqual(len(data["dependencies"]), 2)
        self.assertIn("created_at", data)

    def test_analysis_with_r4r_data(self):
        """Test serialization of r4r_data JSON field"""
        r4r_data = {
            "r_packages": ["ggplot2"],
            "system_libs": ["libcurl"],
            "files_accessed": 5,
        }
        analysis = ReproducibilityAnalysis.objects.create(
            notebook=self.notebook, r4r_data=r4r_data
        )
        serializer = ReproducibilityAnalysisSerializer(analysis)

        self.assertEqual(serializer.data["r4r_data"]["r_packages"], ["ggplot2"])

    def test_analysis_diff_html_field(self):
        """Test diff_html field serialization"""
        analysis = ReproducibilityAnalysis.objects.create(
            notebook=self.notebook,
            diff_html='<div class="diff">Changes</div>',
        )
        serializer = ReproducibilityAnalysisSerializer(analysis)
        self.assertIn("diff_html", serializer.data)


class UserSerializerTest(TestCase):
    """Test UserSerializer"""

    def test_serialize_user(self):
        """Test user serialization"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass",
            first_name="Test",
            last_name="User",
        )
        serializer = UserSerializer(user)
        data = serializer.data

        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "test@example.com")
        self.assertNotIn("password", data)  # Password should not be exposed

    def test_user_registration_serialization(self):
        """Test user registration data"""
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepass123",
        }
        serializer = UserSerializer(data=user_data)
        self.assertTrue(serializer.is_valid())

    def test_user_validation_duplicate_username(self):
        """Test validation prevents duplicate usernames"""
        User.objects.create_user(username="existing", password="test")

        duplicate_data = {
            "username": "existing",
            "email": "new@example.com",
            "password": "test123",
        }
        serializer = UserSerializer(data=duplicate_data)
        self.assertFalse(serializer.is_valid())
