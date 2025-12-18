import subprocess
import tempfile
import os
import shutil
import re
import json
import time
import datetime
import zipfile
import hashlib
import traceback

# 🔥 Import the Analyzer
from .static_analyzer import ReproducibilityAnalyzer


class RExecutor:
    def __init__(self):
        self.analyzer = ReproducibilityAnalyzer()

    def execute_rmd(self, content, notebook_id):
        start_time = time.time()
        self._log_header(f"EXECUTING NOTEBOOK {notebook_id}")

        # ---------------------------------------------------------
        # 0. CHECK CACHE (Smart Skip)
        # ---------------------------------------------------------
        # If content hasn't changed, we return the previous result immediately.
        final_repro_dir = f"storage/notebooks/{notebook_id}/reproducibility"
        content_hash = self._compute_content_hash(content)
        hash_file = os.path.join(final_repro_dir, ".content_hash")

        # Load Static Analysis first (we need it even if cached)
        try:
            static_analysis = self.analyzer.analyze(content or "")
        except Exception:
            static_analysis = {"issues": [], "total_issues": 0}

        if os.path.exists(final_repro_dir) and os.path.exists(hash_file):
            try:
                stored_hash = open(hash_file, "r").read().strip()
                if stored_hash == content_hash:
                    self._log(
                        "✅ Content unchanged. Using CACHED result.", level="INFO"
                    )

                    html_content = self.read_file(final_repro_dir, "notebook.html")
                    # If HTML is empty, cache might be broken, so we re-run
                    if html_content:
                        return {
                            "success": True,
                            "build_success": True,
                            "html": html_content,
                            "dockerfile": self.read_file(final_repro_dir, "Dockerfile"),
                            "makefile": self.read_file(final_repro_dir, "Makefile"),
                            "manifest": self.read_json(
                                final_repro_dir, "manifest.json"
                            ),
                            "logs": "Cached result (content unchanged)",
                            "detected_packages": self.detect_packages_from_content(
                                content
                            ),
                            "static_analysis": static_analysis,
                            "cached": True,
                        }
            except Exception:
                self._log("⚠️ Cache read failed. Re-running.", level="WARN")

        # ---------------------------------------------------------
        # 1. PREPARATION
        # ---------------------------------------------------------
        self._log_section("1. PREPARATION")

        # Log Static Analysis Results
        self._log(
            f"Static Analysis: {static_analysis.get('total_issues', 0)} issues found"
        )

        with tempfile.TemporaryDirectory(dir="/tmp") as temp_dir:
            self._log(f"Working Directory: {temp_dir}")

            rmd_path = os.path.join(temp_dir, "notebook.Rmd")
            try:
                with open(rmd_path, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                return self._error_response("Failed to save Rmd file", e)

            # ---------------------------------------------------------
            # 2. PACKAGE INSTALLATION (Optimized)
            # ---------------------------------------------------------
            packages = self.detect_packages_from_content(content)
            if packages:
                self._log(f"Checking {len(packages)} R packages...")

                # 🔥 OPTIMIZED INSTALLATION COMMAND
                # It loops through packages and only installs if 'require' fails.
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
                        "⚠️ Package installation warning (proceeding anyway)",
                        level="WARN",
                    )

            # ---------------------------------------------------------
            # 3. HTML RENDERING
            # ---------------------------------------------------------
            self._log_section("3. HTML RENDERING")

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
                    render_res.stderr
                    + "\n"
                    + render_res.stdout,  # Combine logs for better debugging
                    static_analysis=static_analysis,
                )

            html_content = self.read_file(temp_dir, "notebook.html")

            # ---------------------------------------------------------
            # 4. R4R TRACING (Generate Dockerfile)
            # ---------------------------------------------------------
            self._log_section("4. R4R FULL EXECUTION")
            r4r_output_dir = os.path.join(temp_dir, "r4r_output")

            r4r_binary = "/usr/local/bin/r4r"
            if not os.path.exists(r4r_binary):
                r4r_binary = "/usr/bin/r4r"

            env = os.environ.copy()
            env["HOME"] = "/home/r4r"
            env["VISUAL"] = "/bin/true"

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

            # Note: r4r might fail on some complex cases, but if we have HTML, we treat it as partial success usually.
            # But for a strict system, let's report error if it fails completely.

            # ---------------------------------------------------------
            # 5. SAVING RESULTS (Update Cache)
            # ---------------------------------------------------------
            self._log_section("5. SAVING RESULTS")
            os.makedirs(final_repro_dir, exist_ok=True)

            try:
                # Save r4r output (Dockerfile, Makefile, manifest)
                if os.path.exists(r4r_output_dir):
                    shutil.copytree(r4r_output_dir, final_repro_dir, dirs_exist_ok=True)

                # Save HTML and Rmd manually just in case r4r missed them
                with open(os.path.join(final_repro_dir, "notebook.html"), "w") as f:
                    f.write(html_content)
                shutil.copy(rmd_path, os.path.join(final_repro_dir, "notebook.Rmd"))

                # Write Hash to mark this as "Latest Valid State"
                with open(hash_file, "w") as f:
                    f.write(content_hash)

                self._log(f"Files saved to: {final_repro_dir}")

            except Exception as e:
                return self._error_response("Failed to copy result files", e)

            duration = time.time() - start_time
            self._log_header(f"DONE (Took {duration:.2f}s)")

            return {
                "success": True,
                "build_success": r4r_res.returncode == 0,
                "html": html_content,
                "dockerfile": self.read_file(final_repro_dir, "Dockerfile"),
                "makefile": self.read_file(final_repro_dir, "Makefile"),
                "manifest": self.read_json(final_repro_dir, "manifest.json"),
                "logs": r4r_res.stdout + (r4r_res.stderr or ""),
                "detected_packages": packages,
                "static_analysis": static_analysis,
                "cached": False,
            }

    # --- HELPERS ---

    def _compute_content_hash(self, content):
        if not content:
            return ""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _run_command(self, cmd, cwd, desc="Command", env=None, timeout=300):
        cmd_str = " ".join(cmd)
        self._log(f"[{desc}] Running...")
        try:
            result = subprocess.run(
                cmd, cwd=cwd, capture_output=True, text=True, env=env, timeout=timeout
            )
            # Log output logic (truncated for cleanliness)
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
        # Regex for library(pkg), require(pkg), require("pkg")
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
                        if file.endswith(".zip") or file.startswith(
                            "."
                        ):  # Skip zip itself and hidden files
                            continue
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, repro_dir)
                        zipf.write(file_path, arcname)
            return zip_path
        except Exception as e:
            print(f"Zip failed: {e}")
            return None
