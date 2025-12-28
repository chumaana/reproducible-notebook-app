"""
R Markdown Executor for simple local notebook execution.
Renders R Markdown files to HTML without containerization.
"""

import os
import tempfile
import shutil
import time
from typing import Dict, Any
from .base import BaseExecutor
from ..services.package_manager import RPackageManager
from ..services.storage_manager import StorageManager
from ..static_analyzer import ReproducibilityAnalyzer


class RmdExecutor(BaseExecutor):
    """
    Executor for simple R Markdown rendering in local environment.
    Handles package detection, installation, and HTML generation.
    """

    def __init__(self):
        super().__init__()
        self.package_manager = RPackageManager()
        self.storage_manager = StorageManager()
        self.analyzer = ReproducibilityAnalyzer()

    def execute(self, content: str, notebook_id: int) -> Dict[str, Any]:
        """
        Execute R Markdown and generate HTML output.

        Args:
            content: R Markdown content to execute
            notebook_id: ID of the notebook being executed

        Returns:
            Dictionary containing:
                - success: bool
                - html: str (rendered HTML output)
                - detected_packages: list of R packages used
                - static_analysis: dict with reproducibility issues
                - logs: str (execution logs)
                - error: str (if failed)
        """
        start_time = time.time()
        self._log_header(f"SIMPLE EXECUTION - NOTEBOOK {notebook_id}")

        final_dir = self.storage_manager.get_notebook_dir(notebook_id)

        # Run static analysis
        try:
            static_analysis = self.analyzer.analyze(content or "")
        except Exception:
            static_analysis = {"issues": [], "total_issues": 0}

        with tempfile.TemporaryDirectory(dir="/tmp") as temp_dir:
            # Write R Markdown content to file
            rmd_path = os.path.join(temp_dir, "notebook.Rmd")
            with open(rmd_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Detect and install required packages
            packages = self.package_manager.detect_packages_from_content(content)
            if packages:
                self._log(f"Checking {len(packages)} R packages...")
                install_result = self.package_manager.install_packages(
                    packages, temp_dir
                )
                if install_result.returncode != 0:
                    self._log(
                        "Package installation warning (proceeding anyway)", level="WARN"
                    )

            # Render R Markdown to HTML
            self._log_section("RENDERING HTML")
            render_res = self._run_command(
                cmd=[
                    "R",
                    "-e",
                    "rmarkdown::render('notebook.Rmd', output_file='notebook.html')",
                ],
                cwd=temp_dir,
                desc="RMarkdown Render",
            )

            if render_res.returncode != 0:
                return self._error_response(
                    "RMarkdown Render Failed",
                    render_res.stderr + "\n" + render_res.stdout,
                    static_analysis=static_analysis,
                )

            # Save HTML output and Rmd file
            html_content = self.storage_manager.read_file(temp_dir, "notebook.html")
            self.storage_manager.write_file(
                final_dir, "notebook_local.html", html_content
            )
            shutil.copy(rmd_path, os.path.join(final_dir, "notebook.Rmd"))

            duration = time.time() - start_time
            self._log_header(f"SIMPLE EXECUTION DONE ({duration:.2f}s)")

            return {
                "success": True,
                "html": html_content,
                "detected_packages": packages,
                "static_analysis": static_analysis,
                "logs": render_res.stdout,
            }
