from unittest.mock import patch, MagicMock, mock_open
from django.test import TestCase
from notebooks.services.storage_manager import StorageManager
from notebooks.services.package_manager import RPackageManager


class StorageManagerUnitTest(TestCase):
    """Pure unit tests - exact method names from code"""

    def setUp(self):
        self.storage = StorageManager(base_dir="/fake/base")
        self.notebook_id = 123

    @patch("os.makedirs")
    @patch("os.path.join")
    def test_get_notebook_dir(self, mock_join, mock_makedirs):
        """Test get_notebook_dir"""
        mock_join.return_value = "/fake/base/123/reproducibility"

        path = self.storage.get_notebook_dir(self.notebook_id)

        mock_makedirs.assert_called_once()
        self.assertEqual(path, "/fake/base/123/reproducibility")

    @patch("builtins.open", new_callable=mock_open, read_data="test content")
    @patch("os.path.exists")
    @patch("os.path.join")
    def test_read_file(self, mock_join, mock_exists, mock_file):
        """Test read_file"""
        mock_exists.return_value = True
        mock_join.return_value = "/fake/dir/test.txt"

        content = self.storage.read_file("/fake/dir", "test.txt")

        mock_file.assert_called_once()
        self.assertEqual(content, "test content")

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.join")
    def test_write_file(self, mock_join, mock_file, mock_makedirs):
        """Test write_file   (not save_file)"""
        mock_join.return_value = "/fake/123/test.txt"

        self.storage.write_file("/fake/123", "test.txt", "content")

        mock_makedirs.assert_called_once()
        mock_file.assert_called_once_with("/fake/123/test.txt", "w", encoding="utf-8")


class RPackageManagerUnitTest(TestCase):
    """Pure unit tests - exact methods from code"""

    def setUp(self):
        self.manager = RPackageManager()

    def test_detect_packages_from_content(self):
        """Test detect_packages_from_content"""
        code = 'library(ggplot2)\nrequire("dplyr")\nlibrary(tidyr)'
        deps = self.manager.detect_packages_from_content(code)

        self.assertEqual(deps, ["dplyr", "ggplot2", "tidyr"])

    def test_detect_packages_from_content_empty(self):
        """Test empty content"""
        deps = self.manager.detect_packages_from_content("")
        self.assertEqual(deps, [])

    @patch("subprocess.run")
    def test_install_packages(self, mock_run):
        """Test install_packages"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "success"
        mock_run.return_value = mock_result

        result = self.manager.install_packages(["ggplot2"], "/tmp")

        mock_run.assert_called_once()
        self.assertIn("ggplot2", mock_run.call_args[0][0][2])


class StorageManagerErrorTest(TestCase):
    """Test error paths"""

    def setUp(self):
        self.storage = StorageManager()

    @patch("os.path.exists")
    def test_read_file_nonexistent(self, mock_exists):
        """Nonexistent file returns empty string"""
        mock_exists.return_value = False

        content = self.storage.read_file("/fake", "missing.txt")
        self.assertEqual(content, "")
