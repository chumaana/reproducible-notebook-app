import subprocess
import tempfile
import os
import shutil
import re
import json
import time
import datetime, zipfile
import hashlib


class RExecutor:
    def execute_rmd(self, content, notebook_id):
        start_time = time.time()
        self._log_header(f"EXECUTING NOTEBOOK {notebook_id}")

        self._log_section("0. STATIC ANALYSIS")
        static_analysis = self.analyzer.analyze(content)

        self._log(f"Static Analysis: {static_analysis['total_issues']} issues found")
        for issue in static_analysis["issues"]:
            level = "ERROR" if issue["severity"] == "high" else "WARN"
            self._log(
                f"[{issue['severity'].upper()}] {issue['title']}: {issue['details']}",
                level=level,
            )
        with tempfile.TemporaryDirectory(dir="/tmp") as temp_dir:
            self._log(f"Working Directory: {temp_dir}")

            self._log_section("1. PREPARATION")

            rmd_path = os.path.join(temp_dir, "notebook.Rmd")
            try:
                with open(rmd_path, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                return self._error_response("Failed to save Rmd file", e)

            packages = self.detect_packages_from_content(content)
            if packages:
                pkgs_str = "', '".join(packages)
                self._log("Installing R packages...")
                self._run_command(
                    cmd=[
                        "R",
                        "-e",
                        f"install.packages(c('{pkgs_str}'), repos='https://cloud.r-project.org/', quiet=FALSE)",
                    ],
                    cwd=temp_dir,
                    desc="Install Packages",
                )

            self._log_section("2. HTML RENDERING")

            html_path = os.path.join(temp_dir, "notebook.html")
            render_res = self._run_command(
                cmd=["R", "-e", "rmarkdown::render('notebook.Rmd')"],
                cwd=temp_dir,
                desc="RMarkdown Render",
            )

            if render_res.returncode != 0:
                return self._error_response(
                    "RMarkdown Render Failed", render_res.stderr
                )

            html_content = self.read_file(temp_dir, "notebook.html")

            final_repro_dir = f"storage/notebooks/{notebook_id}/reproducibility"
            content_hash = self._compute_content_hash(content)
            hash_file = os.path.join(final_repro_dir, ".content_hash")

            if os.path.exists(final_repro_dir) and os.path.exists(hash_file):
                stored_hash = open(hash_file, "r").read().strip()

                if stored_hash == content_hash:
                    self._log(
                        "✅ r4r package already exists for this content (SKIP r4r)",
                        level="INFO",
                    )

                    dockerfile = self.read_file(final_repro_dir, "Dockerfile")
                    makefile = self.read_file(final_repro_dir, "Makefile")
                    manifest = self.read_json(final_repro_dir, "manifest.json")

                    duration = time.time() - start_time
                    self._log_header(f"DONE (Cached, Took {duration:.2f}s)")

                    return {
                        "success": True,
                        "build_success": True,
                        "html": html_content,
                        "dockerfile": dockerfile,
                        "makefile": makefile,
                        "manifest": manifest,
                        "logs": "Cached reproducibility package (content unchanged)",
                        "detected_packages": packages,
                        "static_analysis": static_analysis,
                        "cached": True,
                    }
                else:
                    self._log(
                        "Content changed, regenerating r4r package...", level="INFO"
                    )

            self._log_section("3. R4R FULL EXECUTION")

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

            full_log = r4r_res.stdout + (r4r_res.stderr or "")

            if r4r_res.returncode != 0:
                return self._error_response(
                    "r4r Execution Failed",
                    r4r_res.stderr,
                    html=html_content,
                )

            self._log_section("4. SAVING RESULTS")

            os.makedirs(final_repro_dir, exist_ok=True)

            try:
                shutil.copytree(r4r_output_dir, final_repro_dir, dirs_exist_ok=True)
                shutil.copy(rmd_path, os.path.join(final_repro_dir, "notebook.Rmd"))

                with open(hash_file, "w") as f:
                    f.write(content_hash)

                self._log(f"Files saved to: {final_repro_dir}")
                self._log(f"Content hash saved: {content_hash}")
            except Exception as e:
                return self._error_response("Failed to copy files", e)

            dockerfile = self.read_file(final_repro_dir, "Dockerfile")
            makefile = self.read_file(final_repro_dir, "Makefile")
            manifest = self.read_json(final_repro_dir, "manifest.json")

            duration = time.time() - start_time
            self._log_header(f"DONE (Took {duration:.2f}s)")

            return {
                "success": True,
                "build_success": True,
                "html": html_content,
                "dockerfile": dockerfile,
                "makefile": makefile,
                "manifest": manifest,
                "logs": full_log,
                "detected_packages": packages,
                "static_analysis": static_analysis,
                "cached": False,
            }

    def _compute_content_hash(self, content):

        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    #     def _get_missing_packages(self, packages):

    #         if not packages:
    #             return []

    #         check_script = f"""
    # installed <- installed.packages()[, "Package"]
    # required <- c('{("', '").join(packages)}')
    # missing <- required[!required %in% installed]
    # if (length(missing) > 0) {{
    #     cat(paste(missing, collapse='\\n'))
    # }} else {{
    #     cat('')
    # }}
    # """

    #         try:
    #             result = subprocess.run(
    #                 ["R", "--vanilla", "--quiet", "-e", check_script],
    #                 capture_output=True,
    #                 text=True,
    #                 timeout=10,
    #             )

    #             if result.returncode == 0:
    #                 missing = result.stdout.strip().split("\n")
    #                 missing = [pkg.strip() for pkg in missing if pkg.strip()]
    #                 return missing
    #             else:
    #                 self._log(
    #                     "Package check failed, will install all packages", level="WARN"
    #                 )
    #                 return packages

    #         except Exception as e:
    #             self._log(f"Package check error: {e}, will install all", level="WARN")
    #             return packages

    def _run_command(self, cmd, cwd, desc="Command", env=None, timeout=300):
        cmd_str = " ".join(cmd)
        self._log(f"[{desc}] Running: {cmd_str[:150]}...")
        try:
            result = subprocess.run(
                cmd, cwd=cwd, capture_output=True, text=True, env=env, timeout=timeout
            )

            if result.stdout:
                print(f"[{desc} STDOUT] {result.stdout[:200]}...", flush=True)
            if result.stderr:
                print(f"[{desc} STDERR] {result.stderr[:500]}...", flush=True)

            if result.returncode == 0:
                self._log(f"[{desc}] Success")
            else:
                self._log(f"[{desc}] Failed (Exit: {result.returncode})", level="ERROR")
                err_text = result.stderr or ""
                self._log(f"STDERR TAIL:\n{err_text[-1000:]}", level="DEBUG")

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

    def _error_response(self, msg, detail, html=""):
        return {"success": False, "error": f"{msg}: {detail}", "html": html}

    def read_file(self, d, f):
        p = os.path.join(d, f)
        return open(p).read() if os.path.exists(p) else ""

    def read_json(self, d, f):
        p = os.path.join(d, f)
        return json.load(open(p)) if os.path.exists(p) else {}

    def detect_packages_from_content(self, c):
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
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, repro_dir)
                        zipf.write(file_path, arcname)
            return zip_path
        except Exception:
            return None
