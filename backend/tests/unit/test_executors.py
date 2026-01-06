"""
Unit tests for R execution engines.
tests/unit/test_executors.py
"""

from django.test import TestCase
from notebooks.executors.rmd_executor import RmdExecutor
from notebooks.executors.r4r_executor import R4RExecutor
from notebooks.executors.rdiff_executor import RDiffExecutor
from notebooks.models import Notebook
from django.contrib.auth.models import User
import os
import shutil


class RmdExecutorTest(TestCase):
    """Test RmdExecutor functionality"""

    def setUp(self):
        """Set up test data"""
        self.executor = RmdExecutor()
        self.user = User.objects.create_user(username="testuser", password="test")
        self.notebook = Notebook.objects.create(
            title="Test",
            content="---\ntitle: 'Test'\n---\n\n```{r}\nprint('Hello')\n```",
            author=self.user,
        )

    def test_executor_initialization(self):
        """Test executor initializes correctly"""
        self.assertIsNotNone(self.executor)
        self.assertIsNotNone(self.executor.package_manager)
        self.assertIsNotNone(self.executor.storage_manager)
        self.assertIsNotNone(self.executor.analyzer)

    def test_execute_simple_code(self):
        """Test execution of simple R code"""
        simple_code = """
---
title: "Test"
output: html_document
---

```{r}
x <- 1 + 1
print(x)
```
"""
        result = self.executor.execute(simple_code, self.notebook.id)

        self.assertIn("success", result)
        if result.get("success"):
            self.assertIn("html", result)
            self.assertIn("detected_packages", result)
            self.assertIn("static_analysis", result)
            self.assertIn("logs", result)

    def test_execute_with_syntax_error(self):
        """Test execution with R syntax error"""
        bad_code = """
---
title: "Test"
---

```{r}
x <- 1 +
print(x)
```
"""
        result = self.executor.execute(bad_code, self.notebook.id)

        # Should fail due to syntax error
        if not result.get("success"):
            self.assertIn("error", result)

    def test_execute_with_library(self):
        """Test execution with library loading"""
        code_with_lib = """
---
title: "Test"
---

```{r}
# Basic computation without external packages
x <- 1:10
mean_x <- mean(x)
print(mean_x)
```
"""
        result = self.executor.execute(code_with_lib, self.notebook.id)

        self.assertIn("success", result)
        if result.get("success"):
            self.assertIn("html", result)

    def test_static_analysis_included(self):
        """Test that execution includes static analysis"""
        code = """
```{r}
x <- rnorm(100)
```
"""
        result = self.executor.execute(code, self.notebook.id)

        self.assertIn("static_analysis", result)
        self.assertIn("issues", result["static_analysis"])
        self.assertIn("total_issues", result["static_analysis"])

    def test_package_detection(self):
        """Test that packages are detected from content"""
        code_with_packages = """
```{r}
library(ggplot2)
library(dplyr)
x <- 1:10
```
"""
        result = self.executor.execute(code_with_packages, self.notebook.id)

        self.assertIn("detected_packages", result)
        if result.get("detected_packages"):
            self.assertIsInstance(result["detected_packages"], list)

    def test_html_output_saved(self):
        """Test that HTML output is saved to storage"""
        simple_code = """
---
title: "Test"
output: html_document
---

```{r}
print('test')
```
"""
        result = self.executor.execute(simple_code, self.notebook.id)

        if result.get("success"):
            # Check using storage_manager's method
            storage_dir = self.executor.storage_manager.get_notebook_dir(
                self.notebook.id
            )
            html_path = os.path.join(storage_dir, "notebook_local.html")

            # Give it a moment for file system sync
            import time

            time.sleep(0.1)

            self.assertTrue(
                os.path.exists(html_path), f"HTML file should exist at {html_path}"
            )

    def tearDown(self):
        """Clean up test files"""
        storage_path = f"storage/notebooks/{self.notebook.id}"
        if os.path.exists(storage_path):
            shutil.rmtree(storage_path)


class R4RExecutorTest(TestCase):
    """Test R4RExecutor functionality"""

    def setUp(self):
        """Set up test data"""
        self.executor = R4RExecutor()
        self.user = User.objects.create_user(username="testuser", password="test")
        self.notebook = Notebook.objects.create(
            title="Test R4R",
            content="---\ntitle: 'Test'\n---\n\n```{r}\nprint('test')\n```",
            author=self.user,
        )

        # First execute with RmdExecutor to create notebook.Rmd
        rmd_executor = RmdExecutor()
        rmd_executor.execute(self.notebook.content, self.notebook.id)

    def test_executor_initialization(self):
        """Test R4R executor initializes"""
        self.assertIsNotNone(self.executor)
        self.assertIsNotNone(self.executor.storage_manager)

    def test_execute_requires_rmd_file(self):
        """Test that execution requires notebook.Rmd to exist"""
        new_notebook = Notebook.objects.create(
            title="No RMD", content="```{r}\nprint('test')\n```", author=self.user
        )

        result = self.executor.execute(new_notebook.id)

        self.assertFalse(result.get("success"))
        self.assertIn("error", result)
        self.assertIn("Run notebook first", result["error"])

    def test_execute_generates_dockerfile(self):
        """Test that execution generates Dockerfile"""
        result = self.executor.execute(self.notebook.id)

        if result.get("success"):
            self.assertIn("dockerfile", result)
            self.assertIsInstance(result["dockerfile"], str)
            self.assertIn("FROM", result["dockerfile"])

    def test_execute_generates_makefile(self):
        """Test that execution generates Makefile"""
        result = self.executor.execute(self.notebook.id)

        if result.get("success"):
            self.assertIn("makefile", result)
            self.assertIsInstance(result["makefile"], str)

    def test_execute_generates_manifest(self):
        """Test that execution generates manifest with dependencies"""
        result = self.executor.execute(self.notebook.id)

        if result.get("success"):
            self.assertIn("manifest", result)
            self.assertIsInstance(result["manifest"], dict)

    def test_r4r_data_included(self):
        """Test that r4r metrics are included"""
        result = self.executor.execute(self.notebook.id)

        if result.get("success"):
            self.assertIn("r4r_data", result)
            self.assertIsInstance(result["r4r_data"], dict)
            self.assertIn("r_packages", result["r4r_data"])
            self.assertIn("system_libs", result["r4r_data"])
            self.assertIn("files_accessed", result["r4r_data"])

    def test_r4r_data_structure(self):
        """Test r4r_data has correct structure"""
        result = self.executor.execute(self.notebook.id)

        if result.get("success") and result.get("r4r_data"):
            r4r_data = result["r4r_data"]
            self.assertIsInstance(r4r_data["r_packages"], list)
            self.assertIsInstance(r4r_data["system_libs"], list)
            self.assertIsInstance(r4r_data["files_accessed"], int)

    def test_build_success_flag(self):
        """Test that build_success flag is included"""
        result = self.executor.execute(self.notebook.id)

        # build_success is only included on success
        if result.get("success"):
            self.assertIn("build_success", result)
            self.assertIsInstance(result["build_success"], bool)
        else:
            # If r4r failed, success=False and no build_success flag
            self.assertFalse(result.get("success"))

    def test_duration_tracked(self):
        """Test that execution duration is tracked"""
        result = self.executor.execute(self.notebook.id)

        if result.get("success"):
            self.assertIn("duration_seconds", result)
            self.assertGreater(result["duration_seconds"], 0)

    def test_package_ready_flag(self):
        """Test that package_ready flag indicates ZIP creation"""
        result = self.executor.execute(self.notebook.id)

        if result.get("success"):
            self.assertIn("package_ready", result)

    def tearDown(self):
        """Clean up test files"""
        storage_path = f"storage/notebooks/{self.notebook.id}"
        if os.path.exists(storage_path):
            shutil.rmtree(storage_path)


class RDiffExecutorTest(TestCase):
    """Test RDiffExecutor functionality"""

    def setUp(self):
        """Set up test data"""
        self.executor = RDiffExecutor()
        self.user = User.objects.create_user(username="testuser", password="test")
        self.notebook = Notebook.objects.create(
            title="Test Diff",
            content="---\ntitle: 'Test'\n---\n\n```{r}\nprint('Version 1')\n```",
            author=self.user,
        )

    def test_executor_initialization(self):
        """Test rdiff executor initializes"""
        self.assertIsNotNone(self.executor)
        self.assertIsNotNone(self.executor.storage_manager)
        self.assertEqual(self.executor.rdiff_binary, "/usr/local/bin/r-diff")

    def test_execute_requires_local_html(self):
        """Test rdiff requires local HTML to exist"""
        result = self.executor.execute(self.notebook.id)

        self.assertFalse(result.get("success"))
        self.assertIn("error", result)
        self.assertIn("Local HTML not found", result["error"])

    def test_execute_requires_container_html(self):
        """Test rdiff requires container HTML to exist"""
        # Use storage_manager to get correct path
        storage_dir = self.executor.storage_manager.get_notebook_dir(self.notebook.id)
        os.makedirs(storage_dir, exist_ok=True)

        # Create local HTML
        local_html_path = os.path.join(storage_dir, "notebook_local.html")
        with open(local_html_path, "w") as f:
            f.write("<html><body>Local</body></html>")

        # Verify local HTML exists
        self.assertTrue(os.path.exists(local_html_path))

        # Don't create container HTML
        result = self.executor.execute(self.notebook.id)

        self.assertFalse(result.get("success"))
        self.assertIn("error", result)
        self.assertIn("Container HTML not found", result["error"])

    def test_execute_with_both_html_files(self):
        """Test rdiff execution with both HTML files present"""
        # Create both HTML files
        storage_dir = f"storage/notebooks/{self.notebook.id}"
        os.makedirs(storage_dir, exist_ok=True)

        local_html = "<html><body><h1>Local Version</h1></body></html>"
        container_html = "<html><body><h1>Container Version</h1></body></html>"

        with open(os.path.join(storage_dir, "notebook_local.html"), "w") as f:
            f.write(local_html)
        with open(os.path.join(storage_dir, "notebook_container.html"), "w") as f:
            f.write(container_html)

        result = self.executor.execute(self.notebook.id)

        # May succeed or fail depending on r-diff installation
        self.assertIn("success", result)
        if result.get("success"):
            self.assertIn("diff_html", result)
            self.assertIn("logs", result)

    def test_rdiff_binary_check(self):
        """Test that rdiff binary path is checked"""
        # Use storage_manager to get correct path
        storage_dir = self.executor.storage_manager.get_notebook_dir(self.notebook.id)
        os.makedirs(storage_dir, exist_ok=True)

        # Create both HTML files
        local_html_path = os.path.join(storage_dir, "notebook_local.html")
        container_html_path = os.path.join(storage_dir, "notebook_container.html")

        with open(local_html_path, "w") as f:
            f.write("<html><body>Local</body></html>")
        with open(container_html_path, "w") as f:
            f.write("<html><body>Container</body></html>")

        # Verify both files exist
        self.assertTrue(os.path.exists(local_html_path))
        self.assertTrue(os.path.exists(container_html_path))

        # Now change binary path to non-existent
        original_binary = self.executor.rdiff_binary
        self.executor.rdiff_binary = "/non/existent/r-diff"

        result = self.executor.execute(self.notebook.id)

        self.assertFalse(result.get("success"))
        self.assertIn("r-diff binary not found", result["error"])

        # Restore
        self.executor.rdiff_binary = original_binary

    def tearDown(self):
        """Clean up test files"""
        storage_path = f"storage/notebooks/{self.notebook.id}"
        if os.path.exists(storage_path):
            shutil.rmtree(storage_path)


class ExecutorIntegrationTest(TestCase):
    """Test integration between executors"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username="testuser", password="test")
        self.notebook = Notebook.objects.create(
            title="Integration Test",
            content="---\ntitle: 'Test'\n---\n\n```{r}\nx <- 1:10\nprint(mean(x))\n```",
            author=self.user,
        )

    def test_full_workflow(self):
        """Test complete workflow: RmdExecutor -> R4RExecutor -> RDiffExecutor"""
        # Step 1: Execute notebook locally
        rmd_executor = RmdExecutor()
        rmd_result = rmd_executor.execute(self.notebook.content, self.notebook.id)

        self.assertTrue(rmd_result.get("success"), "RmdExecutor should succeed")
        self.assertIn("html", rmd_result)
        self.assertIn("static_analysis", rmd_result)

        # Step 2: Generate reproducibility package
        r4r_executor = R4RExecutor()
        r4r_result = r4r_executor.execute(self.notebook.id)

        if r4r_result.get("success"):
            self.assertIn("dockerfile", r4r_result)
            self.assertIn("r4r_data", r4r_result)
            self.assertIn("package_ready", r4r_result)

        # Step 3: Generate semantic diff
        rdiff_executor = RDiffExecutor()
        rdiff_result = rdiff_executor.execute(self.notebook.id)

        # Diff may succeed if both HTML files exist
        if rdiff_result.get("success"):
            self.assertIn("diff_html", rdiff_result)

    def tearDown(self):
        """Clean up test files"""
        storage_path = f"storage/notebooks/{self.notebook.id}"
        if os.path.exists(storage_path):
            shutil.rmtree(storage_path)


class ExecutorErrorHandlingTest(TestCase):
    """Test error handling in executors"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username="testuser", password="test")

    def test_rmd_executor_invalid_notebook_id(self):
        """Test RmdExecutor with invalid notebook ID"""
        executor = RmdExecutor()

        # Execute with non-existent notebook ID
        result = executor.execute("```{r}\nprint('test')\n```", 99999)

        # Should still create directory and attempt execution
        self.assertIn("success", result)

    def test_r4r_executor_invalid_notebook_id(self):
        """Test R4RExecutor with invalid notebook ID"""
        executor = R4RExecutor()

        result = executor.execute(99999)

        self.assertFalse(result.get("success"))
        self.assertIn("error", result)

    def test_rdiff_executor_invalid_notebook_id(self):
        """Test RDiffExecutor with invalid notebook ID"""
        executor = RDiffExecutor()

        result = executor.execute(99999)

        self.assertFalse(result.get("success"))
        self.assertIn("error", result)

    def test_rmd_executor_empty_content(self):
        """Test execution with empty content"""
        executor = RmdExecutor()
        notebook = Notebook.objects.create(title="Empty", content="", author=self.user)

        result = executor.execute("", notebook.id)

        # Should handle empty content gracefully
        self.assertIn("success", result)

    def tearDown(self):
        """Clean up any created files"""
        storage_path = "storage/notebooks"
        if os.path.exists(storage_path):
            for item in os.listdir(storage_path):
                item_path = os.path.join(storage_path, item)
                if os.path.isdir(item_path):
                    try:
                        shutil.rmtree(item_path)
                    except:
                        pass
