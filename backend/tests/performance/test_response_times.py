"""
API Response Time Benchmarks

Tests all endpoints with realistic data volumes and measures latency.
Sets performance thresholds based on endpoint complexity.
tests/performance/test_response_times.py
"""

import time
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from notebooks.models import Notebook, Execution, ReproducibilityAnalysis


class ResponseTimeThresholds:
    """Performance targets for different endpoint types"""

    LIST = 0.5  # List endpoints: 500ms
    DETAIL = 0.2  # Single item retrieval: 200ms
    CREATE = 0.3  # Create operations: 300ms
    UPDATE = 0.3  # Update operations: 300ms
    AUTH = 0.5  # Authentication operations: 500ms (includes password hashing)
    EXECUTE = 10.0  # Code execution: 10s (slow operation)
    DOWNLOAD = 0.5  # File downloads: 500ms


class AuthEndpointResponseTimeTest(TestCase):
    """Test authentication endpoint response times"""

    def setUp(self):
        self.client = APIClient()
        User.objects.create_user(
            username="existing", email="existing@test.com", password="password123"
        )

    def test_register_response_time(self):
        """Registration should complete quickly"""
        data = {
            "username": "newuser",
            "email": "new@test.com",
            "password": "ComplexPass123!",
        }

        start = time.time()
        response = self.client.post("/api/auth/register/", data)
        duration = time.time() - start

        self.assertEqual(response.status_code, 201)
        self.assertLess(
            duration,
            ResponseTimeThresholds.AUTH,
            f"Registration took {duration:.3f}s (threshold: {ResponseTimeThresholds.CREATE}s)",
        )

    def test_login_response_time(self):
        """Login should be fast"""
        data = {"username": "existing", "password": "password123"}

        start = time.time()
        response = self.client.post("/api/auth/login/", data)
        duration = time.time() - start

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            duration,
            ResponseTimeThresholds.AUTH,
            f"Login took {duration:.3f}s (threshold: {ResponseTimeThresholds.DETAIL}s)",
        )

    def test_profile_get_response_time(self):
        """Profile retrieval should be fast"""
        user = User.objects.get(username="existing")
        self.client.force_authenticate(user=user)

        start = time.time()
        response = self.client.get("/api/auth/profile/")
        duration = time.time() - start

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            duration,
            ResponseTimeThresholds.DETAIL,
            f"Profile GET took {duration:.3f}s (threshold: {ResponseTimeThresholds.DETAIL}s)",
        )


class NotebookListResponseTimeTest(TestCase):
    """Test notebook list endpoint with varying data volumes"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

    def test_empty_list_response_time(self):
        """Empty list should be extremely fast"""
        start = time.time()
        response = self.client.get("/api/notebooks/")
        duration = time.time() - start

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            duration, 0.1, f"Empty list took {duration:.3f}s"  # 100ms for empty list
        )

    def test_list_10_notebooks_response_time(self):
        """List 10 notebooks should be fast"""
        # Create 10 notebooks
        for i in range(10):
            Notebook.objects.create(
                title=f"Notebook {i}",
                content=f"# Content {i}\n```{{r}}\nprint({i})\n```",
                author=self.user,
            )

        start = time.time()
        response = self.client.get("/api/notebooks/")
        duration = time.time() - start

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)
        self.assertLess(
            duration,
            ResponseTimeThresholds.LIST,
            f"10 notebooks took {duration:.3f}s (threshold: {ResponseTimeThresholds.LIST}s)",
        )

    def test_list_50_notebooks_response_time(self):
        """List 50 notebooks with executions"""
        notebooks = []
        for i in range(50):
            nb = Notebook.objects.create(
                title=f"NB {i}", content=f"# {i}", author=self.user
            )
            notebooks.append(nb)
            # Add execution to half of them
            if i % 2 == 0:
                Execution.objects.create(
                    notebook=nb, status="completed", html_output="<html>Test</html>"
                )

        start = time.time()
        response = self.client.get("/api/notebooks/")
        duration = time.time() - start

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 10)
        self.assertLess(
            duration,
            ResponseTimeThresholds.LIST * 1.5,  # Allow 50% more time for 50 items
            f"50 notebooks took {duration:.3f}s (threshold: {ResponseTimeThresholds.LIST * 1.5}s)",
        )


class NotebookDetailResponseTimeTest(TestCase):
    """Test individual notebook retrieval performance"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

    def test_simple_notebook_response_time(self):
        """Simple notebook retrieval should be very fast"""
        notebook = Notebook.objects.create(
            title="Simple", content="# Test", author=self.user
        )

        start = time.time()
        response = self.client.get(f"/api/notebooks/{notebook.id}/")
        duration = time.time() - start

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            duration,
            ResponseTimeThresholds.DETAIL,
            f"Simple notebook took {duration:.3f}s (threshold: {ResponseTimeThresholds.DETAIL}s)",
        )

    def test_notebook_with_executions_response_time(self):
        """Notebook with execution history"""
        notebook = Notebook.objects.create(
            title="With Executions", content="# Test", author=self.user
        )
        # Add 10 executions
        for i in range(10):
            Execution.objects.create(
                notebook=notebook,
                status="completed",
                html_output=f"<html>Output {i}</html>",
            )

        start = time.time()
        response = self.client.get(f"/api/notebooks/{notebook.id}/")
        duration = time.time() - start

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            duration,
            ResponseTimeThresholds.DETAIL,
            f"Notebook with 10 executions took {duration:.3f}s",
        )

    def test_large_content_notebook_response_time(self):
        """Notebook with large content (100KB)"""
        large_content = "# Large Content\n" + ("x" * 100 + "\n") * 1000  # ~100KB
        notebook = Notebook.objects.create(
            title="Large Content", content=large_content, author=self.user
        )

        start = time.time()
        response = self.client.get(f"/api/notebooks/{notebook.id}/")
        duration = time.time() - start

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            duration,
            ResponseTimeThresholds.DETAIL * 2,  # Allow 2x time for large content
            f"Large notebook took {duration:.3f}s",
        )


class NotebookMutationResponseTimeTest(TestCase):
    """Test create/update/delete performance"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

    def test_create_notebook_response_time(self):
        """Notebook creation should be fast"""
        data = {
            "title": "New Notebook",
            "content": "# Test\n```{r}\nprint('hello')\n```",
        }

        start = time.time()
        response = self.client.post("/api/notebooks/", data, format="json")
        duration = time.time() - start

        self.assertEqual(response.status_code, 201)
        self.assertLess(
            duration,
            ResponseTimeThresholds.CREATE,
            f"Create took {duration:.3f}s (threshold: {ResponseTimeThresholds.CREATE}s)",
        )

    def test_update_notebook_response_time(self):
        """Notebook updates should be fast"""
        notebook = Notebook.objects.create(
            title="Original", content="# Original", author=self.user
        )

        data = {"title": "Updated Title"}

        start = time.time()
        response = self.client.patch(
            f"/api/notebooks/{notebook.id}/", data, format="json"
        )
        duration = time.time() - start

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            duration,
            ResponseTimeThresholds.UPDATE,
            f"Update took {duration:.3f}s (threshold: {ResponseTimeThresholds.UPDATE}s)",
        )

    def test_toggle_public_response_time(self):
        """Toggle public status should be fast"""
        notebook = Notebook.objects.create(
            title="Test", content="# Test", author=self.user
        )

        start = time.time()
        response = self.client.post(f"/api/notebooks/{notebook.id}/toggle_public/")
        duration = time.time() - start

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            duration,
            ResponseTimeThresholds.UPDATE,
            f"Toggle public took {duration:.3f}s",
        )


class ExecutionHistoryResponseTimeTest(TestCase):
    """Test execution history endpoint performance"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

    def test_executions_endpoint_response_time(self):
        """Execution history should load quickly"""
        notebook = Notebook.objects.create(
            title="Test", content="# Test", author=self.user
        )
        # Create 20 executions
        executions = []
        for i in range(20):
            executions.append(
                Execution(
                    notebook=notebook,
                    status="completed",
                    html_output=f"<html>Output {i}</html>",
                )
            )
        Execution.objects.bulk_create(executions)

        start = time.time()
        response = self.client.get(f"/api/notebooks/{notebook.id}/executions/")
        duration = time.time() - start

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 20)
        self.assertLess(
            duration,
            ResponseTimeThresholds.LIST,
            f"20 executions took {duration:.3f}s (threshold: {ResponseTimeThresholds.LIST}s)",
        )


class ReproducibilityEndpointResponseTimeTest(TestCase):
    """Test reproducibility analysis endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

    def test_reproducibility_endpoint_response_time(self):
        """Reproducibility data should load quickly"""
        notebook = Notebook.objects.create(
            title="Test", content="# Test", author=self.user
        )
        ReproducibilityAnalysis.objects.create(
            notebook=notebook,
            dependencies=["dplyr", "ggplot2"],
            system_deps=["libcurl"],
            dockerfile="FROM r-base:latest",
            makefile="all:\n\tRscript script.R",
        )

        start = time.time()
        response = self.client.get(f"/api/notebooks/{notebook.id}/reproducibility/")
        duration = time.time() - start

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            duration,
            ResponseTimeThresholds.DETAIL,
            f"Reproducibility took {duration:.3f}s (threshold: {ResponseTimeThresholds.DETAIL}s)",
        )


class PerformanceSummaryTest(TestCase):
    """Generate performance report across all endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

        # Create test data
        self.notebook = Notebook.objects.create(
            title="Test", content="# Test", author=self.user
        )

    def measure_endpoint(self, method, url, data=None):
        """Helper to measure endpoint response time"""
        start = time.time()
        if method == "GET":
            response = self.client.get(url)
        elif method == "POST":
            response = self.client.post(url, data or {}, format="json")
        elif method == "PATCH":
            response = self.client.patch(url, data or {}, format="json")
        duration = time.time() - start
        return response.status_code, duration

    def test_performance_summary(self):
        """Measure and report all endpoint response times"""
        endpoints = [
            ("GET", "/api/notebooks/", "List notebooks"),
            ("GET", f"/api/notebooks/{self.notebook.id}/", "Get notebook"),
            ("POST", "/api/notebooks/", "Create notebook"),
            ("PATCH", f"/api/notebooks/{self.notebook.id}/", "Update notebook"),
            ("GET", f"/api/notebooks/{self.notebook.id}/executions/", "Get executions"),
            ("GET", "/api/auth/profile/", "Get profile"),
        ]

        print("\n" + "=" * 60)
        print("PERFORMANCE SUMMARY")
        print("=" * 60)

        results = []
        for method, url, description in endpoints:
            data = None
            if method == "POST":
                data = {"title": "New", "content": "# Test"}
            elif method == "PATCH":
                data = {"title": "Updated"}

            status, duration = self.measure_endpoint(method, url, data)
            results.append((description, method, status, duration))
            print(f"{description:30} {method:6} {status:3} {duration*1000:7.2f}ms")

        print("=" * 60)

        # All should have succeeded or created
        for desc, method, status, duration in results:
            self.assertIn(status, [200, 201], f"{desc} failed with {status}")
