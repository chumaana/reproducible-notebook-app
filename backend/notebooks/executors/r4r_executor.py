"""
R4R Executor for generating reproducibility packages.
"""

import os
import re
import tarfile
import tempfile
import shutil
import time
from typing import Dict, Any

from .base import BaseExecutor
from ..services.storage_manager import StorageManager


class R4RExecutor(BaseExecutor):
    """
    Executor for R4R reproducibility package generation.
    Traces R package dependencies, system libraries, and file access patterns.
    """

    def __init__(self):
        super().__init__()
        self.storage_manager = StorageManager()

    def execute(self, notebook_id: int) -> Dict[str, Any]:
        """
        Generate reproducibility package using r4r tool.
        Returns dictionary with success status, artifacts (dockerfile, makefile), and metrics.
        """
        start_time = time.time()
        self._log_header(f"GENERATING REPRODUCIBILITY PACKAGE - NOTEBOOK {notebook_id}")

        final_dir = self.storage_manager.get_notebook_dir(notebook_id)

        if not os.path.exists(os.path.join(final_dir, "notebook.Rmd")):
            return {"success": False, "error": "Run notebook first to generate .Rmd"}

        with tempfile.TemporaryDirectory(dir="/tmp") as temp_dir:
            rmd_path = os.path.join(temp_dir, "notebook.Rmd")
            shutil.copy(os.path.join(final_dir, "notebook.Rmd"), rmd_path)

            self._log_section("R4R TRACE & BUILD")
            r4r_output_dir = os.path.join(temp_dir, "r4r_output")

            r4r_binary = "/usr/local/bin/r4r"
            if not os.path.exists(r4r_binary):
                r4r_binary = "/usr/bin/r4r"

            env = os.environ.copy()
            env["HOME"] = "/home/r4r"
            env["VISUAL"] = "/bin/true"  # Prevent interactive prompts

            r4r_cmd = [
                r4r_binary,
                "-v",
                "--output",
                r4r_output_dir,
                "R",
                "-e",
                "rmarkdown::render('notebook.Rmd')",
            ]

            r4r_res = self._run_command(
                cmd=r4r_cmd, cwd=temp_dir, env=env, desc="r4r Trace & Build"
            )

            if r4r_res.returncode != 0:
                return {
                    "success": False,
                    "error": f"r4r failed:\n{r4r_res.stderr}",
                    "logs": r4r_res.stdout + r4r_res.stderr,
                }

            r4r_data = self._collect_r4r_metrics(r4r_output_dir)

            if os.path.exists(r4r_output_dir):
                shutil.copytree(r4r_output_dir, final_dir, dirs_exist_ok=True)

            container_html = self.storage_manager.find_html_file(r4r_output_dir)
            if container_html:
                shutil.copy(
                    container_html, os.path.join(final_dir, "notebook_container.html")
                )

            zip_path = self.storage_manager.create_zip(notebook_id)
            duration = time.time() - start_time
            self._log_header(f"PACKAGE GENERATION DONE ({duration:.2f}s)")

            return {
                "success": True,
                "build_success": r4r_res.returncode == 0,
                "duration_seconds": duration,
                "r4r_data": r4r_data,
                "dockerfile": self.storage_manager.read_file(final_dir, "Dockerfile"),
                "makefile": self.storage_manager.read_file(final_dir, "Makefile"),
                "manifest": self.storage_manager.read_json(final_dir, "manifest.json"),
                "logs": r4r_res.stdout,
                "package_ready": zip_path is not None,
            }

    def _collect_r4r_metrics(self, r4r_output_dir: str) -> dict:
        """Parses R packages, system libraries, and file access counts from output artifacts."""
        metrics = {"r_packages": [], "system_libs": [], "files_accessed": 0}

        # Parse R packages
        r_script = os.path.join(r4r_output_dir, "install_r_packages.R")
        if os.path.exists(r_script):
            with open(r_script, "r") as f:
                found = re.findall(
                    r"remotes::install_version\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]",
                    f.read(),
                )
                metrics["r_packages"] = sorted(
                    [f"{name} ({ver})" for name, ver in found]
                )

        # Parse System Libraries
        dockerfile_path = os.path.join(r4r_output_dir, "Dockerfile")
        libs = set()
        IGNORE_LIST = [
            "RUN",
            "apt-get",
            "install",
            "update",
            "upgrade",
            "&&",
            "\\",
            "sudo",
            "-y",
            "--no-install-recommends",
            "rm",
            "-rf",
            "/var/lib/apt/lists/*",
        ]

        if os.path.exists(dockerfile_path):
            with open(dockerfile_path, "r") as f:
                content_flat = f.read().replace("\\\n", " ")

            matches = re.findall(
                r"apt-get install.*?-y\s+(.*?)(?:&&|;|\n|$)", content_flat
            )
            for match in matches:
                for part in match.split():
                    clean = part.strip()
                    if not clean or clean.startswith("-") or clean in IGNORE_LIST:
                        continue
                    # Remove arch/version suffix (e.g. libxml2:amd64 or pandoc=2.0)
                    libs.add(clean.split(":")[0].split("=")[0])

        metrics["system_libs"] = sorted(list(libs))

        # Count accessed files
        archive_path = os.path.join(r4r_output_dir, "archive.tar")
        if os.path.exists(archive_path):
            try:
                with tarfile.open(archive_path) as tar:
                    metrics["files_accessed"] = len(tar.getmembers())
            except Exception:
                pass

        return metrics
