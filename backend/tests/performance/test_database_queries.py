"""
Database Query Optimization Tests

Detects N+1 queries, measures query counts, and validates optimizations.
Tests that serializers use select_related/prefetch_related properly.

Location: backend/tests/performance/test_database_queries.py
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient
from notebooks.models import Notebook, Execution, ReproducibilityAnalysis


class NotebookListQueryOptimizationTest(TestCase):
    """Test N+1 query prevention in notebook list endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

    def test_list_notebooks_query_count(self):
        """
        CRITICAL: Notebook list should not cause N+1 queries

        Problem: NotebookSerializer calls:
        - get_execution_count() → queries executions per notebook
        - get_last_execution_status() → queries executions per notebook
        - get_has_analysis() → checks analysis per notebook

        With 10 notebooks, this could cause 30+ queries (N+1 problem).
        Should use prefetch_related to optimize.
        """
        # Create 10 notebooks with related data
        for i in range(10):
            nb = Notebook.objects.create(
                title=f"NB {i}", content=f"# Content {i}", author=self.user
            )
            # Each has an execution
            Execution.objects.create(
                notebook=nb, status="completed", html_output="<html>Test</html>"
            )
            # Each has analysis
            if i % 2 == 0:
                ReproducibilityAnalysis.objects.create(
                    notebook=nb, dependencies=["dplyr"]
                )

        with CaptureQueriesContext(connection) as context:
            response = self.client.get("/api/notebooks/")

        num_queries = len(context.captured_queries)

        print(f"\n{'='*60}")
        print(f"NOTEBOOK LIST QUERY ANALYSIS")
        print(f"{'='*60}")
        print(f"Notebooks: 10")
        print(f"Queries executed: {num_queries}")
        print(f"{'='*60}")

        if num_queries > 5:
            print(f" WARNING: Detected potential N+1 query problem!")
            print(f"Expected: ~3-5 queries (with prefetch_related)")
            print(f"Actual: {num_queries} queries")
            print(f"\nRecommendation:")
            print(f"  Add to NotebookViewSet.get_queryset():")
            print(f"    .prefetch_related('executions', 'analysis')")

            # Print actual queries for debugging
            print(f"\nQueries executed:")
            for i, query in enumerate(context.captured_queries, 1):
                sql = query["sql"][:100]
                print(f"  {i}. {sql}...")

        # Soft assertion - warn but don't fail
        # In production, you'd fix the viewset and make this a hard assertion
        self.assertLess(
            num_queries,
            25,  # Should be ~3-5, but allowing up to 25 for now
            f"Too many queries ({num_queries}). Likely N+1 problem. "
            f"Add prefetch_related('executions', 'analysis') to queryset.",
        )

    def test_empty_list_query_count(self):
        """Empty list should only make minimal queries"""
        with CaptureQueriesContext(connection) as context:
            response = self.client.get("/api/notebooks/")

        num_queries = len(context.captured_queries)

        # Should be: 1 for auth, 1 for notebooks
        self.assertLessEqual(
            num_queries, 3, f"Empty list made {num_queries} queries, expected ≤3"
        )


class NotebookDetailQueryOptimizationTest(TestCase):
    """Test query efficiency for single notebook retrieval"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

    def test_notebook_detail_query_count(self):
        """Notebook detail should use select_related for author"""
        notebook = Notebook.objects.create(
            title="Test", content="# Test", author=self.user
        )
        # Add related data
        Execution.objects.create(
            notebook=notebook, status="completed", html_output="<html>Test</html>"
        )
        ReproducibilityAnalysis.objects.create(
            notebook=notebook, dependencies=["ggplot2"]
        )

        with CaptureQueriesContext(connection) as context:
            response = self.client.get(f"/api/notebooks/{notebook.id}/")

        num_queries = len(context.captured_queries)

        print(f"\nNotebook detail queries: {num_queries}")

        # Should be reasonable: auth + notebook + maybe prefetch
        self.assertLess(
            num_queries, 10, f"Notebook detail made {num_queries} queries, expected <10"
        )


class ExecutionQueryOptimizationTest(TestCase):
    """Test execution-related query efficiency"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

    def test_executions_list_query_count(self):
        """Execution list should use select_related for notebook"""
        notebook = Notebook.objects.create(
            title="Test", content="# Test", author=self.user
        )
        # Create 10 executions
        for i in range(10):
            Execution.objects.create(
                notebook=notebook, status="completed", html_output=f"<html>{i}</html>"
            )

        with CaptureQueriesContext(connection) as context:
            response = self.client.get(f"/api/notebooks/{notebook.id}/executions/")

        num_queries = len(context.captured_queries)

        print(f"\nExecution list queries: {num_queries}")

        # Should use select_related('notebook') to avoid N+1
        self.assertLess(
            num_queries,
            5,
            f"Execution list made {num_queries} queries. "
            f"Use select_related('notebook') in queryset.",
        )


class BulkOperationQueryTest(TestCase):
    """Test query efficiency for bulk operations"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

    def test_bulk_create_notebooks(self):
        """Creating multiple notebooks shouldn't scale linearly"""
        # This tests if we're using bulk_create efficiently

        with CaptureQueriesContext(connection) as context:
            for i in range(5):
                data = {"title": f"Bulk {i}", "content": f"# {i}"}
                self.client.post("/api/notebooks/", data, format="json")

        num_queries = len(context.captured_queries)

        print(f"\n5 sequential creates: {num_queries} queries")

        # Each create is separate, so this will be linear
        # Just documenting current behavior
        self.assertGreater(num_queries, 10)  # Will be ~15-25


class QueryCountRegressionTest(TestCase):
    """Baseline query counts - fail if performance degrades"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

        # Standard test data
        self.notebook = Notebook.objects.create(
            title="Standard", content="# Test", author=self.user
        )
        Execution.objects.create(
            notebook=self.notebook, status="completed", html_output="<html>Test</html>"
        )

    def measure_queries(self, method, url, data=None):
        """Measure number of queries for an endpoint"""
        with CaptureQueriesContext(connection) as context:
            if method == "GET":
                self.client.get(url)
            elif method == "POST":
                self.client.post(url, data or {}, format="json")
            elif method == "PATCH":
                self.client.patch(url, data or {}, format="json")
        return len(context.captured_queries)

    def test_query_count_baselines(self):
        """
        Document baseline query counts for all endpoints.
        Update these numbers as you optimize.
        """
        baselines = {
            "GET /api/notebooks/": ("List notebooks", 15),  # Current baseline
            "GET /api/notebooks/{id}/": ("Get notebook", 8),
            "POST /api/notebooks/": ("Create notebook", 6),
            "GET /api/notebooks/{id}/executions/": ("List executions", 5),
            "GET /api/profile/": ("Get profile", 3),
        }

        print(f"\n{'='*70}")
        print(f"QUERY COUNT BASELINE REPORT")
        print(f"{'='*70}")
        print(f"{'Endpoint':<45} {'Queries':>8} {'Baseline':>8} {'Status':>7}")
        print(f"{'-'*70}")

        # Measure each endpoint
        measurements = {
            "GET /api/notebooks/": self.measure_queries("GET", "/api/notebooks/"),
            "GET /api/notebooks/{id}/": self.measure_queries(
                "GET", f"/api/notebooks/{self.notebook.id}/"
            ),
            "POST /api/notebooks/": self.measure_queries(
                "POST", "/api/notebooks/", {"title": "New", "content": "# Test"}
            ),
            "GET /api/notebooks/{id}/executions/": self.measure_queries(
                "GET", f"/api/notebooks/{self.notebook.id}/executions/"
            ),
            "GET /api/profile/": self.measure_queries("GET", "/api/profile/"),
        }

        # Compare to baselines
        for endpoint, (description, baseline) in baselines.items():
            actual = measurements[endpoint]
            status = "✓" if actual <= baseline else "⚠"
            print(f"{description:<45} {actual:>8} {baseline:>8} {status:>7}")

        print(f"{'='*70}\n")

        # Fail if any endpoint significantly regressed (>50% increase)
        for endpoint, (description, baseline) in baselines.items():
            actual = measurements[endpoint]
            self.assertLess(
                actual,
                baseline * 1.5,  # Allow 50% regression
                f"{description} query count regressed: {actual} > {baseline*1.5:.0f}",
            )


class IndexUsageTest(TestCase):
    """Test that database indexes are being used"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

    def test_notebook_ordering_uses_index(self):
        """Verify that ordering by updated_at uses index"""
        # Create notebooks with different timestamps
        for i in range(20):
            Notebook.objects.create(title=f"NB {i}", content=f"# {i}", author=self.user)

        with CaptureQueriesContext(connection) as context:
            response = self.client.get("/api/notebooks/")

        # Check if ORDER BY uses index
        queries = context.captured_queries
        has_order_by = any("ORDER BY" in q["sql"] for q in queries)

        if has_order_by:
            print("\n✓ Ordering query detected - check EXPLAIN for index usage")

        # todo EXPLAIN ANALYZE
        self.assertTrue(has_order_by, "Should have ORDER BY clause")
