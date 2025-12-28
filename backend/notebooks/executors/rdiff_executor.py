"""
R-Diff Executor for generating semantic diffs between execution outputs.
Compares local and container HTML outputs to detect reproducibility issues.
"""

import os
import tempfile
import time
from typing import Dict, Any
from .base import BaseExecutor
from ..services.storage_manager import StorageManager


class RDiffExecutor(BaseExecutor):
    """
    Executor for generating semantic diff between local and container HTML outputs.
    Uses the r-diff tool to compare execution results.
    """

    def __init__(self):
        super().__init__()
        self.storage_manager = StorageManager()
        self.rdiff_binary = "/usr/local/bin/r-diff"

    def execute(self, notebook_id: int) -> Dict[str, Any]:
        """
        Generate semantic diff using r-diff tool.

        Args:
            notebook_id: ID of the notebook to generate diff for

        Returns:
            Dictionary containing:
                - success: bool
                - diff_html: str (HTML visualization of differences)
                - logs: str
                - error: str (if failed)
        """
        start_time = time.time()
        self._log_header(f"GENERATING SEMANTIC DIFF - NOTEBOOK {notebook_id}")

        final_dir = self.storage_manager.get_notebook_dir(notebook_id)
        local_html = os.path.abspath(os.path.join(final_dir, "notebook_local.html"))
        container_html = os.path.abspath(
            os.path.join(final_dir, "notebook_container.html")
        )

        # Verify both HTML files exist
        if not os.path.exists(local_html):
            return {
                "success": False,
                "error": "Local HTML not found. Run notebook first.",
            }

        if not os.path.exists(container_html):
            return {
                "success": False,
                "error": "Container HTML not found. Generate package first.",
            }

        if not os.path.exists(self.rdiff_binary):
            return {"success": False, "error": "r-diff binary not found"}

        with tempfile.TemporaryDirectory(dir="/tmp") as temp_dir:
            diff_output = os.path.join(temp_dir, "semantic_diff.html")

            diff_cmd = [
                self.rdiff_binary,
                "-html",
                local_html,
                container_html,
                "-output",
                diff_output,
            ]

            diff_res = self._run_command(diff_cmd, cwd=temp_dir, desc="Running r-diff")

            self._log(f"r-diff exit code: {diff_res.returncode}")
            self._log(f"r-diff stdout:\n{diff_res.stdout}")
            self._log(f"r-diff stderr:\n{diff_res.stderr}")

            if diff_res.returncode != 0 or not os.path.exists(diff_output):
                return {
                    "success": False,
                    "error": f"r-diff failed:\n{diff_res.stderr}",
                    "logs": diff_res.stdout + diff_res.stderr,
                }

            # Read and save diff HTML
            diff_html_content = self.storage_manager.read_file(
                temp_dir, "semantic_diff.html"
            )
            self.storage_manager.write_file(
                final_dir, "semantic_diff.html", diff_html_content
            )

            duration = time.time() - start_time
            self._log_header(f"DIFF GENERATION DONE ({duration:.2f}s)")

            return {
                "success": True,
                "diff_html": diff_html_content,
                "logs": diff_res.stdout,
            }
