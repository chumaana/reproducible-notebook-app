import os
import tempfile
import shutil
import time
from typing import Dict, Any

from .base import BaseExecutor
from ..services.storage_manager import StorageManager


class R4RExecutor(BaseExecutor):
    """Executor for R4R reproducibility package generation"""

    def __init__(self):
        super().__init__()
        self.storage_manager = StorageManager()

    def execute(self, notebook_id: int) -> Dict[str, Any]:
        """Generate reproducibility package using r4r"""
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
            env["VISUAL"] = "/bin/true"

            html_path = os.path.join(temp_dir, "result.html")

            r4r_cmd = [
                r4r_binary,
                "-v",
                "--output",
                r4r_output_dir,
                "--result",
                html_path,
                "R",
                "-e",
                "rmarkdown::render('notebook.Rmd')",
            ]

            r4r_res = self._run_command(
                cmd=r4r_cmd,
                cwd=temp_dir,
                env=env,
                timeout=600,
                desc="r4r Trace & Build",
            )

            if r4r_res.returncode != 0:
                return {
                    "success": False,
                    "error": f"r4r failed:\n{r4r_res.stderr}",
                    "logs": r4r_res.stdout + r4r_res.stderr,
                }

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
                "dockerfile": self.storage_manager.read_file(final_dir, "Dockerfile"),
                "makefile": self.storage_manager.read_file(final_dir, "Makefile"),
                "manifest": self.storage_manager.read_json(final_dir, "manifest.json"),
                "logs": r4r_res.stdout,
                "package_ready": zip_path is not None,
            }
