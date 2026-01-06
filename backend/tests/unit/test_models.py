"""
Unit tests for Django models
tests/unit/test_models.py
"""

from django.test import TestCase
from django.contrib.auth.models import User
from notebooks.models import Notebook, Execution, ReproducibilityAnalysis
from datetime import datetime
from django.utils import timezone


class NotebookModelTest(TestCase):
    """Test Notebook model"""

    def setUp(self):
        """Set up test user and notebook"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.notebook = Notebook.objects.create(
            title="Test Notebook", content="# Test\n``````", author=self.user
        )

    def test_notebook_creation(self):
        """Test notebook is created correctly"""
        self.assertEqual(self.notebook.title, "Test Notebook")
        self.assertEqual(self.notebook.author, self.user)
        self.assertIsNotNone(self.notebook.created_at)
        self.assertIsNotNone(self.notebook.updated_at)
        self.assertFalse(self.notebook.is_public)  # Default is False

    def test_notebook_str_representation(self):
        """Test string representation of notebook"""
        expected = f"Test Notebook (testuser)"
        self.assertEqual(str(self.notebook), expected)

    def test_notebook_update_timestamp(self):
        """Test that updated_at changes when notebook is modified"""
        original_updated = self.notebook.updated_at
        # Add small delay to ensure timestamp difference
        import time

        time.sleep(0.01)
        self.notebook.title = "Updated Title"
        self.notebook.save()
        self.assertGreater(self.notebook.updated_at, original_updated)

    def test_notebook_cascade_delete(self):
        """Test that deleting user deletes their notebooks"""
        notebook_id = self.notebook.id
        self.user.delete()
        with self.assertRaises(Notebook.DoesNotExist):
            Notebook.objects.get(id=notebook_id)

    def test_notebook_public_flag(self):
        """Test public/private notebook flag"""
        self.assertFalse(self.notebook.is_public)
        self.notebook.is_public = True
        self.notebook.save()
        self.assertTrue(self.notebook.is_public)


class ExecutionModelTest(TestCase):
    """Test Execution model"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test")
        self.notebook = Notebook.objects.create(
            title="Test", content="``````", author=self.user
        )
        self.execution = Execution.objects.create(
            notebook=self.notebook,
            status="pending",
            html_output="",
            error_message="",
        )

    def test_execution_creation(self):
        """Test execution is created with correct defaults"""
        self.assertEqual(self.execution.status, "pending")
        self.assertEqual(self.execution.html_output, "")
        self.assertIsNotNone(self.execution.started_at)
        self.assertIsNone(self.execution.completed_at)  # Not completed yet

    def test_execution_status_transitions(self):
        """Test execution status can transition correctly"""
        self.execution.status = "running"
        self.execution.save()
        self.assertEqual(self.execution.status, "running")

        self.execution.status = "completed"
        self.execution.html_output = "<html>Result</html>"
        self.execution.completed_at = timezone.now()
        self.execution.save()
        self.assertEqual(self.execution.status, "completed")
        self.assertIsNotNone(self.execution.completed_at)

    def test_execution_failure(self):
        """Test execution can record errors"""
        self.execution.status = "failed"
        self.execution.error_message = "R error: package not found"
        self.execution.completed_at = timezone.now()
        self.execution.save()
        self.assertEqual(self.execution.status, "failed")
        self.assertIn("package not found", self.execution.error_message)

    def test_multiple_executions_per_notebook(self):
        """Test notebook can have multiple executions"""
        Execution.objects.create(notebook=self.notebook, status="completed")
        Execution.objects.create(notebook=self.notebook, status="completed")
        self.assertEqual(self.notebook.executions.count(), 3)

    def test_execution_duration_property(self):
        """Test execution duration calculation"""
        # Without completion time
        self.assertIsNone(self.execution.duration)

        # With completion time
        self.execution.completed_at = self.execution.started_at + timezone.timedelta(
            seconds=5.5
        )
        self.execution.save()
        self.assertEqual(self.execution.duration, 5.5)

    def test_execution_str_representation(self):
        """Test string representation of execution"""
        result = str(self.execution)
        self.assertIn("Test", result)
        self.assertIn("pending", result)


class ReproducibilityAnalysisModelTest(TestCase):
    """Test ReproducibilityAnalysis model"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test")
        self.notebook = Notebook.objects.create(
            title="Test Analysis", content="``````", author=self.user
        )

    def test_analysis_creation(self):
        """Test analysis is created correctly"""
        analysis = ReproducibilityAnalysis.objects.create(
            notebook=self.notebook,
            dockerfile="FROM rocker/r-ver:4.3.0",
            dependencies=["ggplot2", "dplyr"],
        )
        self.assertEqual(analysis.notebook, self.notebook)
        self.assertIsNotNone(analysis.dockerfile)
        self.assertEqual(len(analysis.dependencies), 2)
        self.assertIsNotNone(analysis.created_at)

    def test_analysis_with_dependencies(self):
        """Test analysis stores R package dependencies"""
        deps = ["ggplot2", "dplyr", "tidyr"]
        analysis = ReproducibilityAnalysis.objects.create(
            notebook=self.notebook, dependencies=deps
        )
        self.assertEqual(analysis.dependencies, deps)
        self.assertEqual(len(analysis.dependencies), 3)

    def test_analysis_with_system_deps(self):
        """Test analysis stores system dependencies"""
        sys_deps = ["libcurl4-openssl-dev", "libssl-dev"]
        analysis = ReproducibilityAnalysis.objects.create(
            notebook=self.notebook, system_deps=sys_deps
        )
        self.assertEqual(analysis.system_deps, sys_deps)

    def test_analysis_r4r_data(self):
        """Test analysis stores r4r metrics"""
        r4r_metrics = {
            "r_packages": ["ggplot2", "dplyr"],
            "system_libs": ["libcurl"],
            "files_accessed": ["/data/input.csv"],
        }
        analysis = ReproducibilityAnalysis.objects.create(
            notebook=self.notebook, r4r_data=r4r_metrics
        )
        self.assertEqual(analysis.r4r_data["r_packages"], ["ggplot2", "dplyr"])
        self.assertIn("system_libs", analysis.r4r_data)

    def test_analysis_dockerfile_generation(self):
        """Test Dockerfile generation tracking"""
        dockerfile_content = """FROM rocker/r-ver:4.3.0
RUN R -e "install.packages('ggplot2')"
COPY notebook.Rmd /app/"""

        analysis = ReproducibilityAnalysis.objects.create(
            notebook=self.notebook, dockerfile=dockerfile_content
        )
        self.assertIn("rocker/r-ver", analysis.dockerfile)
        self.assertIn("ggplot2", analysis.dockerfile)

    def test_analysis_makefile_generation(self):
        """Test Makefile generation"""
        makefile_content = '''all: notebook.html
notebook.html: notebook.Rmd
\tRscript -e "rmarkdown::render('notebook.Rmd')"'''

        analysis = ReproducibilityAnalysis.objects.create(
            notebook=self.notebook, makefile=makefile_content
        )
        self.assertIn("notebook.html", analysis.makefile)

    def test_analysis_diff_html(self):
        """Test diff HTML storage"""
        diff_html = '<div class="diff">Change detected</div>'
        analysis = ReproducibilityAnalysis.objects.create(
            notebook=self.notebook, diff_html=diff_html
        )
        self.assertIn("diff", analysis.diff_html)

    def test_analysis_one_to_one_relationship(self):
        """Test one-to-one relationship with notebook"""
        analysis1 = ReproducibilityAnalysis.objects.create(notebook=self.notebook)

        # Refresh notebook to load relationship
        self.notebook.refresh_from_db()

        # Verify one-to-one relationship works
        self.assertIsNotNone(self.notebook.analysis)
        self.assertEqual(self.notebook.analysis.pk, analysis1.pk)

        # Trying to create second analysis should raise IntegrityError
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            ReproducibilityAnalysis.objects.create(notebook=self.notebook)

    def test_analysis_str_representation(self):
        """Test string representation of analysis"""
        analysis = ReproducibilityAnalysis.objects.create(notebook=self.notebook)
        expected = f"Analysis for {self.notebook.title}"
        self.assertEqual(str(analysis), expected)
