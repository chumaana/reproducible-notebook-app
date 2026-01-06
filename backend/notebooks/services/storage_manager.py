"""
Storage Manager service for file system operations.
Handles notebook file storage, reading/writing, and ZIP package creation.
"""

import os
import json
import zipfile
from typing import Optional, Dict, Any


class StorageManager:
    """
    Service for managing notebook file storage and operations.
    Handles directory structure, file I/O, and package creation.
    """

    def __init__(self, base_dir: str = "storage/notebooks"):
        """
        Initialize storage manager with base directory.

        Args:
            base_dir: Root directory for notebook storage
        """
        self.base_dir = base_dir

    def get_notebook_dir(
        self, notebook_id: int, subdir: str = "reproducibility"
    ) -> str:
        """
        Get path to notebook directory, creating it if it doesn't exist.

        Args:
            notebook_id: ID of the notebook
            subdir: Subdirectory name within notebook folder

        Returns:
            Absolute path to notebook directory
        """
        path = os.path.join(self.base_dir, str(notebook_id), subdir)
        os.makedirs(path, exist_ok=True)
        return path

    def read_file(self, directory: str, filename: str) -> str:
        """
        Read text file from directory.

        Args:
            directory: Directory path
            filename: Name of file to read

        Returns:
            File content as string, or empty string if file doesn't exist
        """
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            with open(path, "r", errors="ignore") as f:
                return f.read()
        return ""

    def read_json(self, directory: str, filename: str) -> Dict[str, Any]:
        """
        Read and parse JSON file from directory.

        Args:
            directory: Directory path
            filename: Name of JSON file to read

        Returns:
            Parsed JSON as dictionary, or empty dict if file doesn't exist or is invalid
        """
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def write_file(self, directory: str, filename: str, content: str):
        """
        Write text content to file, creating directory if needed.

        Args:
            directory: Directory path
            filename: Name of file to write
            content: Text content to write
        """
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def create_zip(self, notebook_id: int) -> Optional[str]:
        """
        Create ZIP archive of reproducibility package for download.
        Excludes temporary files and other ZIPs.

        Args:
            notebook_id: ID of the notebook to package

        Returns:
            Path to created ZIP file, or None if creation failed
        """
        repro_dir = self.get_notebook_dir(notebook_id, "reproducibility")
        zip_path = os.path.join(
            self.base_dir, str(notebook_id), "reproducibility_package.zip"
        )

        if not os.path.exists(repro_dir):
            return None

        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(repro_dir):
                    for file in files:
                        # Exclude ZIP files, hidden files, and diff HTML
                        if (
                            file.endswith(".zip")
                            or file.startswith(".")
                            or file == "semantic_diff.html"
                        ):
                            continue

                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, repro_dir)
                        zipf.write(file_path, arcname)

            return zip_path
        except Exception as e:
            print(f"Zip creation failed: {e}")
            return None

    def find_html_file(self, directory: str) -> Optional[str]:
        """
        Find first HTML file in directory tree.

        Args:
            directory: Directory to search

        Returns:
            Path to HTML file, or None if not found
        """
        if not os.path.exists(directory):
            return None

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".html"):
                    return os.path.join(root, file)

        return None
