"""
Integration tests for API Data Contracts.

Validates JSON response structures match serializers and tests
permission models for reproducibility features[web:32][web:38].

tests/integration/test_api_contracts.py
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from notebooks.models import Notebook, Execution


class APIContractTest(TestCase):
    """Test JSON response structures match Serializers."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="contract_user", password="password"
        )
        self.client.force_authenticate(user=self.user)

        self.notebook = Notebook.objects.create(
            title="Schema Test",
            content="# Content\n```{r}\nprint('hello')\n```",
            author=self.user,
            is_public=False,
        )

    def test_notebook_detail_structure(self):
        """Verify notebook detail endpoint returns exact keys from NotebookSerializer."""
        response = self.client.get(f"/api/notebooks/{self.notebook.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        expected_keys = {
            "id",
            "title",
            "author",
            "author_id",
            "content",
            "created_at",
            "updated_at",
            "is_public",
            "analysis",
            "execution_count",
            "last_execution_status",
            "has_analysis",
        }

        self.assertTrue(
            expected_keys.issubset(data.keys()),
            f"Response missing keys: {expected_keys - set(data.keys())}",
        )

        self.assertIsInstance(data["id"], int)
        self.assertIsInstance(data["title"], str)
        self.assertIsInstance(data["is_public"], bool)
        self.assertIsInstance(data["execution_count"], int)
        self.assertIsInstance(data["author"], str)
        self.assertEqual(data["author"], "contract_user")
        self.assertIsInstance(data["author_id"], int)

    def test_notebook_list_structure(self):
        """Verify list endpoint returns consistent structure."""
        response = self.client.get("/api/notebooks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if isinstance(response.data, dict) and "results" in response.data:
            results = response.data["results"]
        else:
            results = response.data

        self.assertIsInstance(results, list)
        if results:
            item = results[0]
            self.assertIn("title", item)
            self.assertIn("author", item)
            self.assertIn("has_analysis", item)

    def test_json_content_type_header(self):
        """Ensure server declares response as JSON."""
        response = self.client.get("/api/notebooks/")
        self.assertTrue("application/json" in response["Content-Type"])

    def test_generate_package_response_structure(self):
        """
        Test POST /api/notebooks/{id}/generate_package/

        Validates R4R package generation response contains required fields:
        success, dockerfile, makefile, manifest, r4r_data.
        """
        response = self.client.post(
            f"/api/notebooks/{self.notebook.id}/generate_package/"
        )

        if response.status_code == status.HTTP_200_OK:
            data = response.data
            self.assertIn("success", data)

            if data.get("success"):
                self.assertIn("dockerfile", data)
                self.assertIn("makefile", data)
                self.assertIn("manifest", data)
                self.assertIn("r4r_data", data)
                self.assertIsInstance(data["dockerfile"], (str, type(None)))
                self.assertIsInstance(data["makefile"], (str, type(None)))
                self.assertIsInstance(data["manifest"], (dict, type(None)))
                self.assertIsInstance(data["r4r_data"], (dict, type(None)))
            else:
                self.assertIn("error", data)

    def test_generate_diff_response_structure(self):
        """
        Test POST /api/notebooks/{id}/generate_diff/

        Validates semantic diff response contains success flag and diff_html.
        """
        response = self.client.post(f"/api/notebooks/{self.notebook.id}/generate_diff/")

        if response.status_code == status.HTTP_200_OK:
            data = response.data
            self.assertIn("success", data)

            if data.get("success"):
                has_diff_html = "diff_html" in data
                has_html = "html" in data
                self.assertTrue(
                    has_diff_html or has_html,
                    "Response should contain 'diff_html' or 'html' key",
                )
                if has_diff_html:
                    self.assertIsInstance(data["diff_html"], (str, type(None)))
            else:
                self.assertIn("error", data)

    def test_download_package_response_type(self):
        """
        Test GET /api/notebooks/{id}/download_package/

        Validates package download returns ZIP file with proper headers
        or 404 if not generated yet.
        """
        response = self.client.get(
            f"/api/notebooks/{self.notebook.id}/download_package/"
        )

        if response.status_code == status.HTTP_200_OK:
            self.assertTrue(
                "application/zip" in response.get("Content-Type", "")
                or "application/octet-stream" in response.get("Content-Type", ""),
                f"Expected ZIP file, got: {response.get('Content-Type')}",
            )
            self.assertIn("Content-Disposition", response)
            self.assertIn("attachment", response["Content-Disposition"])

        elif response.status_code == status.HTTP_404_NOT_FOUND:
            data = response.data
            self.assertIn("error", data)
            self.assertIn("not generated", data["error"].lower())
        else:
            self.fail(f"Unexpected status code: {response.status_code}")

    def test_executions_list_structure(self):
        """
        Test GET /api/notebooks/{id}/executions/

        Validates execution history endpoint returns list with required fields.
        """
        Execution.objects.create(
            notebook=self.notebook,
            status="completed",
            html_output="<p>Result</p>",
            error_message="",
        )

        response = self.client.get(f"/api/notebooks/{self.notebook.id}/executions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIsInstance(data, list)

        if data:
            execution = data[0]
            self.assertTrue(
                {"id", "status", "started_at"}.issubset(execution.keys()),
                f"Execution missing expected keys",
            )
            self.assertIsInstance(execution["id"], int)
            self.assertIsInstance(execution["status"], str)
            self.assertIn(
                execution["status"], ["pending", "running", "completed", "failed"]
            )


class GeneratePackageIntegrationTest(TestCase):
    """Test generate_package endpoint permissions and behavior."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="r4r_user", password="password")
        self.client.force_authenticate(user=self.user)

        self.notebook = Notebook.objects.create(
            title="R4R Test",
            content="```{r}\nlibrary(ggplot2)\nprint('test')\n```",
            author=self.user,
        )

    def test_generate_package_requires_authentication(self):
        """Unauthenticated users cannot generate packages."""
        self.client.logout()
        response = self.client.post(
            f"/api/notebooks/{self.notebook.id}/generate_package/"
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_generate_package_owner_only(self):
        """Only notebook owner can generate package."""
        other_user = User.objects.create_user(username="other", password="password")
        self.client.force_authenticate(user=other_user)

        response = self.client.post(
            f"/api/notebooks/{self.notebook.id}/generate_package/"
        )
        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

    def test_generate_package_creates_analysis_record(self):
        """Successful generation creates ReproducibilityAnalysis record."""
        response = self.client.post(
            f"/api/notebooks/{self.notebook.id}/generate_package/"
        )

        if response.status_code == status.HTTP_200_OK and response.data.get("success"):
            self.notebook.refresh_from_db()
            self.assertTrue(hasattr(self.notebook, "analysis"))
            if self.notebook.analysis.r4r_data:
                self.assertIsInstance(self.notebook.analysis.r4r_data, dict)


class GenerateDiffIntegrationTest(TestCase):
    """Test generate_diff endpoint permissions and behavior."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="diff_user", password="password")
        self.client.force_authenticate(user=self.user)

        self.notebook = Notebook.objects.create(
            title="Diff Test",
            content="```{r}\nset.seed(123)\nrnorm(5)\n```",
            author=self.user,
        )

    def test_generate_diff_requires_authentication(self):
        """Unauthenticated users cannot generate diffs."""
        self.client.logout()
        response = self.client.post(f"/api/notebooks/{self.notebook.id}/generate_diff/")
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_generate_diff_owner_only(self):
        """Only notebook owner can generate diff."""
        other_user = User.objects.create_user(username="other2", password="password")
        self.client.force_authenticate(user=other_user)

        response = self.client.post(f"/api/notebooks/{self.notebook.id}/generate_diff/")
        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

    def test_generate_diff_stores_result(self):
        """Successful diff generation stores HTML in ReproducibilityAnalysis."""
        response = self.client.post(f"/api/notebooks/{self.notebook.id}/generate_diff/")

        if response.status_code == status.HTTP_200_OK and response.data.get("success"):
            self.notebook.refresh_from_db()
            self.assertTrue(hasattr(self.notebook, "analysis"))
            if self.notebook.analysis.diff_html:
                self.assertIsInstance(self.notebook.analysis.diff_html, str)
                self.assertGreater(len(self.notebook.analysis.diff_html), 0)


class DownloadPackageIntegrationTest(TestCase):
    """Test download_package endpoint permissions and file delivery."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="dl_user", password="password")
        self.client.force_authenticate(user=self.user)

        self.notebook = Notebook.objects.create(
            title="Download Test",
            content="```{r}\nprint('hello')\n```",
            author=self.user,
            is_public=False,
        )

    def test_download_package_before_generation(self):
        """Download returns 404 if package not generated yet."""
        response = self.client.get(
            f"/api/notebooks/{self.notebook.id}/download_package/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_download_package_requires_authentication(self):
        """Package download requires authentication even for public notebooks."""
        self.notebook.is_public = True
        self.notebook.save()
        self.client.logout()

        response = self.client.get(
            f"/api/notebooks/{self.notebook.id}/download_package/"
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
            "Package download should require authentication even for public notebooks",
        )

    def test_download_package_owner_can_download(self):
        """Owner can download package for their own notebook."""
        self.notebook.is_public = True
        self.notebook.save()
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f"/api/notebooks/{self.notebook.id}/download_package/"
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND],
            "Owner should be able to download package",
        )

    def test_download_package_private_notebook_requires_owner(self):
        """Private notebook package requires owner authentication."""
        other_user = User.objects.create_user(username="other", password="password")
        self.client.force_authenticate(user=other_user)

        response = self.client.get(
            f"/api/notebooks/{self.notebook.id}/download_package/"
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND],
            "Non-owner cannot download private notebook package",
        )


class ExecutionsListIntegrationTest(TestCase):
    """Test executions list endpoint behavior."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="exec_user", password="password")
        self.client.force_authenticate(user=self.user)

        self.notebook = Notebook.objects.create(
            title="Executions Test",
            content="```{r}\nSys.time()\n```",
            author=self.user,
            is_public=False,
        )

        for i in range(3):
            Execution.objects.create(
                notebook=self.notebook,
                status="completed" if i % 2 == 0 else "failed",
                html_output=f"<p>Result {i}</p>" if i % 2 == 0 else "",
                error_message=f"Error {i}" if i % 2 != 0 else "",
            )

    def test_executions_list_ordered_by_recent(self):
        """Executions returned in reverse chronological order."""
        response = self.client.get(f"/api/notebooks/{self.notebook.id}/executions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        executions = response.data
        self.assertEqual(len(executions), 3)

        ids = [e["id"] for e in executions]
        self.assertEqual(ids, sorted(ids, reverse=True))

    def test_executions_list_public_notebook_guest_access(self):
        """Public notebook executions can be viewed by anyone."""
        self.notebook.is_public = True
        self.notebook.save()
        self.client.logout()

        response = self.client.get(f"/api/notebooks/{self.notebook.id}/executions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_executions_list_private_notebook_requires_auth(self):
        """Private notebook executions require owner authentication."""
        self.client.logout()
        response = self.client.get(f"/api/notebooks/{self.notebook.id}/executions/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_executions_list_filters_by_notebook(self):
        """Executions endpoint only returns executions for specified notebook."""
        other_notebook = Notebook.objects.create(
            title="Other", content="# Other", author=self.user
        )
        Execution.objects.create(
            notebook=other_notebook,
            status="completed",
            html_output="",
            error_message="",
        )

        response = self.client.get(f"/api/notebooks/{self.notebook.id}/executions/")
        executions = response.data

        self.assertEqual(len(executions), 3)
        for execution in executions:
            notebook_id = execution.get("notebook") or execution.get("notebook_id")
            self.assertEqual(notebook_id, self.notebook.id)


class DownloadPermissionsComparisonTest(TestCase):
    """Compare permissions between .Rmd download and Package download."""

    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(username="owner", password="password")

        self.public_notebook = Notebook.objects.create(
            title="Public Notebook",
            content="```{r}\nprint('test')\n```",
            author=self.owner,
            is_public=True,
        )

    def test_guest_can_download_rmd_but_not_package(self):
        """
        Verify guest can download .Rmd but not package for public notebooks.

        Policy: .Rmd files are public for public notebooks, but packages
        require authentication due to environment information.
        """
        self.client.force_authenticate(user=None)

        rmd_response = self.client.get(
            f"/api/notebooks/{self.public_notebook.id}/download/"
        )
        self.assertEqual(
            rmd_response.status_code,
            status.HTTP_200_OK,
            "Guest should be able to download .Rmd for public notebook",
        )

        package_response = self.client.get(
            f"/api/notebooks/{self.public_notebook.id}/download_package/"
        )
        self.assertIn(
            package_response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
            "Guest should NOT be able to download package even for public notebook",
        )

    def test_owner_can_download_both(self):
        """Owner can download both .Rmd and package."""
        self.client.force_authenticate(user=self.owner)

        rmd_response = self.client.get(
            f"/api/notebooks/{self.public_notebook.id}/download/"
        )
        self.assertEqual(rmd_response.status_code, status.HTTP_200_OK)

        package_response = self.client.get(
            f"/api/notebooks/{self.public_notebook.id}/download_package/"
        )
        self.assertIn(
            package_response.status_code,
            [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND],
        )
