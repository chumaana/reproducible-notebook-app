import subprocess
import tempfile
import os
import shutil
import re
import json
import time
import datetime
import zipfile

from .static_analyzer import ReproducibilityAnalyzer


class RExecutor:
    def __init__(self):
        self.analyzer = ReproducibilityAnalyzer()
        self.rdiff_binary = "/usr/local/bin/r-diff"

    def execute_rmd_simple(self, content, notebook_id):
        start_time = time.time()
        self._log_header(f"SIMPLE EXECUTION - NOTEBOOK {notebook_id}")

        final_dir = f"storage/notebooks/{notebook_id}/reproducibility"
        os.makedirs(final_dir, exist_ok=True)

        try:
            static_analysis = self.analyzer.analyze(content or "")
        except Exception:
            static_analysis = {"issues": [], "total_issues": 0}

        with tempfile.TemporaryDirectory(dir="/tmp") as temp_dir:
            rmd_path = os.path.join(temp_dir, "notebook.Rmd")
            with open(rmd_path, "w", encoding="utf-8") as f:
                f.write(content)

            packages = self.detect_packages_from_content(content)
            if packages:
                self._install_packages(packages, temp_dir)

            self._log_section("RENDERING HTML")
            html_path = os.path.join(temp_dir, "notebook.html")
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

            html_content = self.read_file(temp_dir, "notebook.html")

            with open(os.path.join(final_dir, "notebook_local.html"), "w") as f:
                f.write(html_content)
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

    def generate_reproducibility_package(self, notebook_id):
        start_time = time.time()
        self._log_header(f"GENERATING REPRODUCIBILITY PACKAGE - NOTEBOOK {notebook_id}")

        final_dir = f"storage/notebooks/{notebook_id}/reproducibility"

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

            container_html = self._find_html_result(r4r_output_dir)
            if container_html:
                shutil.copy(
                    container_html, os.path.join(final_dir, "notebook_container.html")
                )

            zip_path = self.create_reproducibility_zip(notebook_id)

            duration = time.time() - start_time
            self._log_header(f"PACKAGE GENERATION DONE ({duration:.2f}s)")

            return {
                "success": True,
                "build_success": r4r_res.returncode == 0,
                "dockerfile": self.read_file(final_dir, "Dockerfile"),
                "makefile": self.read_file(final_dir, "Makefile"),
                "manifest": self.read_json(final_dir, "manifest.json"),
                "logs": r4r_res.stdout,
                "package_ready": zip_path is not None,
            }

    def generate_semantic_diff(self, notebook_id):
        """Порівнює local vs container HTML за допомогою r-diff"""
        start_time = time.time()
        self._log_header(f"GENERATING SEMANTIC DIFF - NOTEBOOK {notebook_id}")

        final_dir = f"storage/notebooks/{notebook_id}/reproducibility"

        local_html = os.path.abspath(os.path.join(final_dir, "notebook_local.html"))
        container_html = os.path.abspath(
            os.path.join(final_dir, "notebook_container.html")
        )

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

            diff_html_content = self.read_file(temp_dir, "semantic_diff.html")

            with open(os.path.join(final_dir, "semantic_diff.html"), "w") as f:
                f.write(diff_html_content)

            duration = time.time() - start_time
            self._log_header(f"DIFF GENERATION DONE ({duration:.2f}s)")

            return {
                "success": True,
                "diff_html": diff_html_content,
                "logs": diff_res.stdout,
            }

        packages = self.detect_packages_from_content(content)

    def _install_packages(self, packages, temp_dir):

        if packages:
            self._log(f"Checking {len(packages)} R packages...")

            repo_url = "https://packagemanager.posit.co/cran/__linux__/noble/latest"

            install_script = f"""
                pkgs <- c('{ "', '".join(packages) }')
                repo <- '{repo_url}'
                for (pkg in pkgs) {{
                    if (!require(pkg, character.only = TRUE, quietly = TRUE)) {{
                        message(paste("Installing missing package:", pkg))
                        install.packages(pkg, repos = repo)
                    }} else {{
                        message(paste("Package already installed:", pkg))
                    }}
                }}
                """

            install_res = self._run_command(
                ["R", "-e", install_script],
                cwd=temp_dir,
                desc="Check & Install Packages",
            )

            if install_res.returncode != 0:
                self._log(
                    "Package installation warning (proceeding anyway)",
                    level="WARN",
                )

    def _run_command(self, cmd, cwd, desc="Command", env=None, timeout=300):
        self._log(f"[{desc}] Running...")
        try:
            result = subprocess.run(
                cmd, cwd=cwd, capture_output=True, text=True, env=env, timeout=timeout
            )
            if result.returncode != 0:
                self._log(f"[{desc}] Failed (Exit: {result.returncode})", level="ERROR")
            else:
                self._log(f"[{desc}] Success")
            return result

        except subprocess.TimeoutExpired:
            self._log(f"[{desc}] TIMEOUT", level="ERROR")
            return subprocess.CompletedProcess(
                args=cmd, returncode=124, stdout="", stderr="Timeout"
            )
        except Exception as e:
            self._log(f"[{desc}] Exception: {e}", level="ERROR")
            return subprocess.CompletedProcess(
                args=cmd, returncode=1, stdout="", stderr=str(e)
            )

    def _find_html_result(self, search_dir):
        if not os.path.exists(search_dir):
            return None
        for root, dirs, files in os.walk(search_dir):
            for file in files:
                if file.endswith(".html"):
                    return os.path.join(root, file)
        return None

    def _log(self, msg, level="INFO"):
        print(
            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [{level}] {msg}",
            flush=True,
        )

    def _log_header(self, msg):
        print(f"\n== {msg} ==", flush=True)

    def _log_section(self, msg):
        print(f"\n--- {msg} ---", flush=True)

    def _error_response(self, msg, detail, html="", static_analysis=None):
        return {
            "success": False,
            "error": f"{msg}:\n{detail}",
            "html": html,
            "static_analysis": static_analysis or {},
        }

    def read_file(self, d, f):
        p = os.path.join(d, f)
        if os.path.exists(p):
            with open(p, "r", errors="ignore") as file:
                return file.read()
        return ""

    def read_json(self, d, f):
        p = os.path.join(d, f)
        if os.path.exists(p):
            try:
                return json.load(open(p))
            except:
                return {}
        return {}

    def detect_packages_from_content(self, c):
        if not c:
            return []
        return sorted(
            list(
                set(re.findall(r'(?:library|require)\s*\(\s*["\']?([a-zA-Z0-9\.]+)', c))
            )
        )

    def create_reproducibility_zip(self, notebook_id):
        repro_dir = f"storage/notebooks/{notebook_id}/reproducibility"
        zip_path = f"storage/notebooks/{notebook_id}/reproducibility_package.zip"

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
            print(f"Zip failed: {e}")
            return None
