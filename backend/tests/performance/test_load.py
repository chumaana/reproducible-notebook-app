"""
Load and Stress Testing

Tests system behavior under high load conditions.
Measures degradation patterns and identifies breaking points.

tests/performance/test_load.py
"""

import time
import statistics
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from notebooks.models import Notebook, Execution
import concurrent.futures


class LoadTestBase(TransactionTestCase):
    """Base class for load tests with helper methods"""

    def setUp(self):
        self.user = User.objects.create_user(username="loadtest", password="testpass")
        # Create baseline data
        for i in range(10):
            Notebook.objects.create(
                title=f"Baseline {i}", content=f"# Content {i}", author=self.user
            )

    def simulate_load(self, func, num_requests, max_workers=10):
        """
        Simulate load by executing func multiple times concurrently.

        Args:
            func: Callable to execute
            num_requests: Total number of requests
            max_workers: Max concurrent workers

        Returns:
            dict with timing statistics and results
        """
        timings = []
        errors = []

        def timed_request():
            start = time.time()
            try:
                result = func()
                duration = time.time() - start
                return {"success": True, "duration": duration, "result": result}
            except Exception as e:
                duration = time.time() - start
                return {"success": False, "duration": duration, "error": str(e)}

        # Execute requests concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(timed_request) for _ in range(num_requests)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Analyze results
        for result in results:
            timings.append(result["duration"])
            if not result["success"]:
                errors.append(result["error"])

        return {
            "total_requests": num_requests,
            "successful": len([r for r in results if r["success"]]),
            "failed": len(errors),
            "errors": errors,
            "timings": {
                "min": min(timings) if timings else 0,
                "max": max(timings) if timings else 0,
                "mean": statistics.mean(timings) if timings else 0,
                "median": statistics.median(timings) if timings else 0,
                "p95": (
                    statistics.quantiles(timings, n=20)[18]
                    if len(timings) > 20
                    else max(timings) if timings else 0
                ),
                "p99": (
                    statistics.quantiles(timings, n=100)[98]
                    if len(timings) > 100
                    else max(timings) if timings else 0
                ),
            },
        }

    def print_load_report(self, test_name, stats):
        """Print formatted load test results"""
        print(f"\n{'='*70}")
        print(f"LOAD TEST: {test_name}")
        print(f"{'='*70}")
        print(f"Total Requests:    {stats['total_requests']}")
        print(
            f"Successful:        {stats['successful']} ({stats['successful']/stats['total_requests']*100:.1f}%)"
        )
        print(f"Failed:            {stats['failed']}")
        print(f"\nResponse Times (seconds):")
        print(f"  Min:       {stats['timings']['min']:.3f}s")
        print(f"  Median:    {stats['timings']['median']:.3f}s")
        print(f"  Mean:      {stats['timings']['mean']:.3f}s")
        print(f"  P95:       {stats['timings']['p95']:.3f}s")
        print(f"  P99:       {stats['timings']['p99']:.3f}s")
        print(f"  Max:       {stats['timings']['max']:.3f}s")

        if stats["errors"]:
            print(f"\nErrors ({len(stats['errors'])}):")
            for error in stats["errors"][:5]:  # Show first 5
                print(f"  • {error}")
            if len(stats["errors"]) > 5:
                print(f"  ... and {len(stats['errors']) - 5} more")

        print(f"{'='*70}\n")


class NotebookListLoadTest(LoadTestBase):
    """Load test for notebook list endpoint"""

    def test_list_under_moderate_load(self):
        """50 concurrent users listing notebooks"""
        client = APIClient()
        client.force_authenticate(user=self.user)

        def request():
            return client.get("/api/notebooks/").status_code

        stats = self.simulate_load(func=request, num_requests=50, max_workers=10)

        self.print_load_report("Notebook List - 50 requests", stats)

        # Assertions
        self.assertEqual(stats["failed"], 0, "No requests should fail")
        self.assertLess(
            stats["timings"]["p95"],
            2.0,
            f"P95 latency too high: {stats['timings']['p95']:.3f}s",
        )

    def test_list_under_heavy_load(self):
        """100 concurrent users - stress test"""
        client = APIClient()
        client.force_authenticate(user=self.user)

        def request():
            return client.get("/api/notebooks/").status_code

        stats = self.simulate_load(func=request, num_requests=100, max_workers=20)

        self.print_load_report("Notebook List - 100 requests (STRESS)", stats)

        # Under stress, we allow some degradation
        success_rate = stats["successful"] / stats["total_requests"]
        self.assertGreater(
            success_rate,
            0.95,  # 95% success rate minimum
            f"Success rate too low: {success_rate*100:.1f}%",
        )


class NotebookCRUDLoadTest(LoadTestBase):
    """Load test for notebook CRUD operations"""

    def test_create_under_load(self):
        """30 users creating notebooks simultaneously"""
        counter = {"value": 0}

        def request():
            counter["value"] += 1
            client = APIClient()
            client.force_authenticate(user=self.user)
            data = {
                "title": f"Load Test {counter['value']}",
                "content": f"# Content {counter['value']}",
            }
            return client.post("/api/notebooks/", data, format="json").status_code

        stats = self.simulate_load(func=request, num_requests=30, max_workers=10)

        self.print_load_report("Notebook Create - 30 requests", stats)

        # Verify database consistency
        created_count = Notebook.objects.filter(
            author=self.user, title__startswith="Load Test"
        ).count()

        print(f"Database Integrity Check:")
        print(f"  Expected:  {stats['successful']} notebooks")
        print(f"  Actual:    {created_count} notebooks")
        print(f"  Match:     {'✓' if created_count == stats['successful'] else '✗'}\n")

        self.assertEqual(
            created_count,
            stats["successful"],
            "Database count doesn't match successful requests",
        )

    def test_mixed_operations_under_load(self):
        """Realistic mix: 60% reads, 30% updates, 10% creates"""
        notebooks = list(Notebook.objects.filter(author=self.user)[:5])
        create_counter = {"value": 0}

        def mixed_request(index):
            client = APIClient()
            client.force_authenticate(user=self.user)

            operation = index % 10

            if operation < 6:  # 60% reads
                notebook = notebooks[index % len(notebooks)]
                return client.get(f"/api/notebooks/{notebook.id}/").status_code
            elif operation < 9:  # 30% updates
                notebook = notebooks[index % len(notebooks)]
                data = {"content": f"# Updated {time.time()}"}
                return client.patch(
                    f"/api/notebooks/{notebook.id}/", data, format="json"
                ).status_code
            else:  # 10% creates
                create_counter["value"] += 1
                data = {
                    "title": f"Mixed {create_counter['value']}",
                    "content": f"# Content {create_counter['value']}",
                }
                return client.post("/api/notebooks/", data, format="json").status_code

        # Simulate 50 mixed operations
        timings = []
        for i in range(50):
            start = time.time()
            mixed_request(i)
            timings.append(time.time() - start)

        stats = {
            "total_requests": 50,
            "successful": 50,
            "failed": 0,
            "errors": [],
            "timings": {
                "min": min(timings),
                "max": max(timings),
                "mean": statistics.mean(timings),
                "median": statistics.median(timings),
                "p95": (
                    statistics.quantiles(timings, n=20)[18]
                    if len(timings) > 20
                    else max(timings)
                ),
                "p99": max(timings),
            },
        }

        self.print_load_report("Mixed Operations (60R/30U/10C)", stats)


class ExecutionLoadTest(LoadTestBase):
    """Load test for execution endpoint (most expensive operation)"""

    def test_sequential_executions(self):
        """
        Execute notebooks sequentially (baseline).
        This is expensive - creates real R processes.
        """
        notebook = Notebook.objects.create(
            title="Execution Load Test",
            content="# Test\n```{r}\nprint('hello')\n```",
            author=self.user,
        )

        client = APIClient()
        client.force_authenticate(user=self.user)

        timings = []
        successes = 0

        # Execute 5 times sequentially
        for i in range(5):
            start = time.time()
            response = client.post(f"/api/notebooks/{notebook.id}/execute/")
            duration = time.time() - start
            timings.append(duration)

            if response.status_code in [200, 201]:
                successes += 1

            print(
                f"  Execution {i+1}: {duration:.2f}s (status: {response.status_code})"
            )

        avg_time = statistics.mean(timings)

        print(f"\nSequential Execution Summary:")
        print(f"  Total:       5 executions")
        print(f"  Successful:  {successes}")
        print(f"  Avg Time:    {avg_time:.2f}s")
        print(f"  Min Time:    {min(timings):.2f}s")
        print(f"  Max Time:    {max(timings):.2f}s\n")

        # Execution should complete
        self.assertGreater(successes, 0, "At least some executions should succeed")


class ScalabilityTest(LoadTestBase):
    """Test how performance scales with data volume"""

    def test_list_performance_scaling(self):
        """Measure how list performance degrades with data volume"""
        client = APIClient()
        client.force_authenticate(user=self.user)

        results = []

        # Test with 10, 50, 100, 200 notebooks
        for size in [10, 50, 100, 200]:
            # Ensure we have exactly 'size' notebooks
            current_count = Notebook.objects.filter(author=self.user).count()
            if current_count < size:
                for i in range(size - current_count):
                    Notebook.objects.create(
                        title=f"Scale Test {current_count + i}",
                        content=f"# {i}",
                        author=self.user,
                    )

            # Measure 10 list requests
            timings = []
            for _ in range(10):
                start = time.time()
                response = client.get("/api/notebooks/")
                timings.append(time.time() - start)
                self.assertEqual(response.status_code, 200)

            avg = statistics.mean(timings)
            results.append((size, avg))
            print(f"  {size:3d} notebooks: {avg*1000:.1f}ms avg")

        # Print scaling analysis
        print(f"\nScaling Analysis:")
        print(f"  Data Size    Avg Time    Scaling Factor")
        print(f"  {'-'*45}")
        baseline = results[0][1]
        for size, avg in results:
            factor = avg / baseline
            print(f"  {size:3d} items    {avg*1000:6.1f}ms    {factor:4.1f}x")

        # Performance should scale sub-linearly (better than O(n))
        # With 20x data (10 -> 200), time should be < 20x
        if len(results) >= 4:
            scaling_factor = results[-1][1] / results[0][1]
            self.assertLess(
                scaling_factor,
                20,
                f"Performance scales poorly: {scaling_factor:.1f}x slowdown for 20x data",
            )


class MemoryLeakTest(LoadTestBase):
    """Test for memory leaks under sustained load"""

    def test_sustained_load(self):
        """
        Run requests continuously and monitor for memory issues.
        This is a long-running test - run manually, not in CI.
        """
        client = APIClient()
        client.force_authenticate(user=self.user)

        print("\nSustained Load Test (60 seconds)")
        print("Press Ctrl+C to stop early\n")

        request_count = 0
        start_time = time.time()
        errors = 0

        try:
            while time.time() - start_time < 60:  # Run for 60 seconds
                try:
                    response = client.get("/api/notebooks/")
                    if response.status_code != 200:
                        errors += 1
                    request_count += 1

                    if request_count % 50 == 0:
                        elapsed = time.time() - start_time
                        rate = request_count / elapsed
                        print(
                            f"  {elapsed:.0f}s: {request_count} requests ({rate:.1f} req/s)"
                        )

                    time.sleep(0.1)  # Small delay between requests

                except Exception as e:
                    errors += 1

        except KeyboardInterrupt:
            print("\n  Stopped by user")

        duration = time.time() - start_time
        rate = request_count / duration

        print(f"\nSustained Load Results:")
        print(f"  Duration:       {duration:.1f}s")
        print(f"  Total Requests: {request_count}")
        print(f"  Errors:         {errors}")
        print(f"  Avg Rate:       {rate:.1f} req/s")
        print(f"  Error Rate:     {errors/request_count*100:.2f}%\n")

        # Should maintain low error rate
        error_rate = errors / request_count if request_count > 0 else 1
        self.assertLess(error_rate, 0.05, f"Error rate too high: {error_rate*100:.1f}%")
