import os
import json
import zipfile
from typing import Optional, Dict, Any


class StorageManager:
    """Service for file system operations"""

    def __init__(self, base_dir: str = "storage/notebooks"):
        self.base_dir = base_dir

    def get_notebook_dir(
        self, notebook_id: int, subdir: str = "reproducibility"
    ) -> str:
        """Get path to notebook directory"""
        path = os.path.join(self.base_dir, str(notebook_id), subdir)
        os.makedirs(path, exist_ok=True)
        return path

    def read_file(self, directory: str, filename: str) -> str:
        """Read text file"""
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            with open(path, "r", errors="ignore") as f:
                return f.read()
        return ""

    def read_json(self, directory: str, filename: str) -> Dict[str, Any]:
        """Read JSON file"""
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def write_file(self, directory: str, filename: str, content: str):
        """Write text file"""
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def create_zip(self, notebook_id: int) -> Optional[str]:
        """Create zip archive of reproducibility package"""
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
                        if file.endswith(".zip") or file.startswith("."):
                            continue
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, repro_dir)
                        zipf.write(file_path, arcname)
            return zip_path
        except Exception as e:
            print(f"Zip creation failed: {e}")
            return None

    def find_html_file(self, directory: str) -> Optional[str]:
        """Find HTML file in directory"""
        if not os.path.exists(directory):
            return None

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".html"):
                    return os.path.join(root, file)

        return None
