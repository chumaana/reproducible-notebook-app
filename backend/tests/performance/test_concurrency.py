"""
Concurrency and Race Condition Tests

Tests parallel request handling, race conditions, and data integrity
under concurrent access patterns.

Location: backend/tests/performance/test_concurrency.py
"""

import threading
import time
from django.db import connection, connections
from django.test import TransactionTestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from notebooks.models import Notebook, Execution


class BaseConcurrencyTest(TransactionTestCase):
    """
    Base class for concurrency tests.
    """

    def tearDown(self):
        # Double check to close any lingering main-thread connections
        connections.close_all()
        super().tearDown()


class ConcurrentReadTest(BaseConcurrencyTest):
    """
    Test concurrent read operations (safe operations).
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.notebook = Notebook.objects.create(
            title="Concurrent Read Test", content="# Test", author=self.user
        )

    def test_concurrent_notebook_reads(self):
        """Multiple clients reading same notebook simultaneously"""
        results = []
        errors = []

        def read_notebook():
            """Worker thread function"""
            try:
                client = APIClient()
                client.force_authenticate(user=self.user)
                response = client.get(f"/api/notebooks/{self.notebook.id}/")
                results.append({"status": response.status_code, "data": response.data})
            except Exception as e:
                errors.append(str(e))
            finally:
                connection.close()

        # Spawn 10 concurrent readers
        threads = []
        for _ in range(10):
            t = threading.Thread(target=read_notebook)
            threads.append(t)
            t.start()

        # Wait for all to complete
        for t in threads:
            t.join(timeout=5)

        # All should succeed
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 10)
        for result in results:
            self.assertEqual(result["status"], 200)
            self.assertEqual(result["data"]["id"], self.notebook.id)

    def test_concurrent_list_reads(self):
        """Multiple clients listing notebooks simultaneously"""
        # Create some notebooks
        for i in range(5):
            Notebook.objects.create(title=f"NB {i}", content=f"# {i}", author=self.user)

        results = []
        errors = []

        def list_notebooks():
            try:
                client = APIClient()
                client.force_authenticate(user=self.user)
                response = client.get("/api/notebooks/")
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
            finally:
                connection.close()

        threads = []
        for _ in range(10):
            t = threading.Thread(target=list_notebooks)
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=5)

        self.assertEqual(len(errors), 0)
        self.assertEqual(results.count(200), 10)


class ConcurrentWriteTest(BaseConcurrencyTest):
    """Test concurrent write operations (potential race conditions)"""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_concurrent_notebook_creation(self):
        """Multiple clients creating notebooks simultaneously"""
        created_ids = []
        errors = []
        lock = threading.Lock()

        def create_notebook(index):
            try:
                client = APIClient()
                client.force_authenticate(user=self.user)
                data = {
                    "title": f"Concurrent NB {index}",
                    "content": f"# Content {index}",
                }
                response = client.post("/api/notebooks/", data, format="json")

                with lock:
                    if response.status_code == 201:
                        created_ids.append(response.data["id"])
                    else:
                        errors.append(f"Failed with {response.status_code}")
            except Exception as e:
                with lock:
                    errors.append(str(e))
            finally:
                connection.close()

        # Create 5 notebooks concurrently
        threads = []
        for i in range(5):
            t = threading.Thread(target=create_notebook, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=10)

        # All should succeed
        self.assertEqual(len(errors), 0, f"Errors: {errors}")
        self.assertEqual(len(created_ids), 5)
        self.assertEqual(len(set(created_ids)), 5)

    def test_concurrent_notebook_updates(self):
        """Tests last-write-wins behavior."""
        notebook = Notebook.objects.create(
            title="Original", content="# Original", author=self.user
        )

        results = []
        errors = []
        lock = threading.Lock()

        def update_notebook(new_title):
            try:
                client = APIClient()
                client.force_authenticate(user=self.user)
                data = {"title": new_title}
                response = client.patch(
                    f"/api/notebooks/{notebook.id}/", data, format="json"
                )
                with lock:
                    results.append({"status": response.status_code, "title": new_title})
            except Exception as e:
                with lock:
                    errors.append(str(e))
            finally:
                connection.close()

        # 5 concurrent updates with different titles
        threads = []
        titles = [f"Update {i}" for i in range(5)]
        for title in titles:
            t = threading.Thread(target=update_notebook, args=(title,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=10)

        self.assertEqual(len(errors), 0, f"Errors: {errors}")
        self.assertEqual(len(results), 5)

    def test_concurrent_toggle_public(self):
        """Multiple clients toggling public status."""
        notebook = Notebook.objects.create(
            title="Toggle Test", content="# Test", author=self.user, is_public=False
        )

        results = []
        errors = []
        lock = threading.Lock()

        def toggle_public():
            try:
                client = APIClient()
                client.force_authenticate(user=self.user)
                response = client.post(f"/api/notebooks/{notebook.id}/toggle_public/")
                with lock:
                    results.append(
                        {
                            "status": response.status_code,
                            "is_public": response.data.get("is_public"),
                        }
                    )
            except Exception as e:
                with lock:
                    errors.append(str(e))
            finally:
                connection.close()

        # 10 concurrent toggles
        threads = []
        for _ in range(10):
            t = threading.Thread(target=toggle_public)
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=10)

        self.assertEqual(len(errors), 0, f"Errors: {errors}")
        self.assertEqual(len(results), 10)


class ConcurrentExecutionTest(BaseConcurrencyTest):
    """Test concurrent notebook execution (resource-intensive operation)"""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.notebook = Notebook.objects.create(
            title="Execution Test",
            content="# Test\n```{r}\nprint('hello')\n```",
            author=self.user,
        )

    def test_concurrent_executions_same_notebook(self):
        """Multiple clients executing same notebook simultaneously."""
        results = []
        errors = []
        lock = threading.Lock()

        def execute_notebook():
            try:
                client = APIClient()
                client.force_authenticate(user=self.user)
                response = client.post(f"/api/notebooks/{self.notebook.id}/execute/")
                with lock:
                    results.append(
                        {
                            "status": response.status_code,
                            "success": response.data.get("success", False),
                        }
                    )
            except Exception as e:
                with lock:
                    errors.append(str(e))
            finally:
                connection.close()

        # 3 concurrent executions (realistic load)
        threads = []
        for _ in range(3):
            t = threading.Thread(target=execute_notebook)
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=30)

        print(f"\nConcurrent execution results: {len(results)} completed")
        executions = Execution.objects.filter(notebook=self.notebook)
        self.assertGreaterEqual(executions.count(), 1)


class MixedConcurrencyTest(BaseConcurrencyTest):
    """Test realistic mixed read/write patterns"""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.notebook = Notebook.objects.create(
            title="Mixed Test", content="# Test", author=self.user
        )

    def test_concurrent_reads_and_writes(self):
        """Simulate realistic usage: some clients reading, some writing."""
        results = {"reads": [], "writes": [], "errors": []}
        lock = threading.Lock()

        def read_notebook():
            try:
                client = APIClient()
                client.force_authenticate(user=self.user)
                response = client.get(f"/api/notebooks/{self.notebook.id}/")
                with lock:
                    results["reads"].append(response.status_code)
            except Exception as e:
                with lock:
                    results["errors"].append(f"Read: {e}")
            finally:
                connection.close()

        def update_notebook(index):
            try:
                client = APIClient()
                client.force_authenticate(user=self.user)
                data = {"content": f"# Updated {index}"}
                response = client.patch(
                    f"/api/notebooks/{self.notebook.id}/", data, format="json"
                )
                with lock:
                    results["writes"].append(response.status_code)
            except Exception as e:
                with lock:
                    results["errors"].append(f"Write: {e}")
            finally:
                connection.close()

        # 7 readers, 3 writers
        threads = []
        for _ in range(7):
            threads.append(threading.Thread(target=read_notebook))
        for i in range(3):
            threads.append(threading.Thread(target=update_notebook, args=(i,)))

        for t in threads:
            t.start()

        for t in threads:
            t.join(timeout=10)

        print(f"\nMixed concurrency results:")
        print(f"  Reads: {len(results['reads'])} (expected 7)")
        print(f"  Writes: {len(results['writes'])} (expected 3)")

        self.assertEqual(len(results["errors"]), 0)
        self.assertEqual(len(results["reads"]), 7)
        self.assertEqual(len(results["writes"]), 3)


class DataIntegrityTest(BaseConcurrencyTest):
    """Test that concurrent operations maintain data integrity"""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_notebook_count_integrity(self):
        """Create notebooks concurrently and verify count."""
        created = []
        lock = threading.Lock()

        def create_notebook(index):
            try:
                client = APIClient()
                client.force_authenticate(user=self.user)
                data = {"title": f"NB {index}", "content": f"# {index}"}
                response = client.post("/api/notebooks/", data, format="json")
                if response.status_code == 201:
                    with lock:
                        created.append(response.data["id"])
            except Exception:
                pass
            finally:
                connection.close()

        threads = [
            threading.Thread(target=create_notebook, args=(i,)) for i in range(10)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        actual_count = Notebook.objects.filter(author=self.user).count()
        self.assertEqual(actual_count, len(created))

    def test_execution_count_integrity(self):
        """Verify execution count stays consistent under concurrent access."""
        notebook = Notebook.objects.create(
            title="Integrity Test", content="# Test", author=self.user
        )

        def create_execution(index):
            try:
                Execution.objects.create(
                    notebook=notebook,
                    status="completed",
                    html_output=f"<html>{index}</html>",
                )
            finally:
                connection.close()

        threads = [
            threading.Thread(target=create_execution, args=(i,)) for i in range(5)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        count = Execution.objects.filter(notebook=notebook).count()
        self.assertEqual(count, 5)
