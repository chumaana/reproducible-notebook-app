import subprocess
import tempfile
import os
import shutil
import json


class RExecutor:
    def execute_rmd(self, content, notebook_id):
        temp_dir = tempfile.mkdtemp()

        try:
            rmd_path = os.path.join(temp_dir, "notebook.Rmd")
            with open(rmd_path, "w", encoding="utf-8") as f:
                f.write(content)

            print("Executing with rocker...")
            subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{temp_dir}:/workspace",
                    "-w",
                    "/workspace",
                    "rocker/verse:4.3.3",
                    "R",
                    "-e",
                    "rmarkdown::render('notebook.Rmd')",
                ],
                check=True,
                capture_output=True,
            )

            html_path = os.path.join(temp_dir, "notebook.html")
            if not os.path.exists(html_path):
                return {"success": False, "error": "No HTML from rocker"}

            with open(html_path, "r", encoding="utf-8") as f:
                html = f.read()

            r4r_output_dir = os.path.join(temp_dir, "r4r_output")
            print("Running r4r tracing...")

            result = subprocess.run(
                [
                    "r4r",
                    "--output",
                    r4r_output_dir,
                    "R",
                    "-e",
                    "rmarkdown::render('notebook.Rmd')",
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=600,
            )
            print("r4r stdout:", result.stdout)
            print("r4r stderr:", result.stderr)
            print("r4r return code:", result.returncode)
            print(
                "r4r_output_dir contents:",
                (
                    os.listdir(r4r_output_dir)
                    if os.path.exists(r4r_output_dir)
                    else "EMPTY"
                ),
            )

            dockerfile = self.read_file(r4r_output_dir, "Dockerfile")
            makefile = self.read_file(r4r_output_dir, "Makefile")
            manifest = self.read_json(r4r_output_dir, "manifest.json")
            print(f"Dockerfile length: {len(dockerfile)}")
            print(f"Makefile length: {len(makefile)}")
            self.save_reproducibility_package(
                notebook_id,
                {"dockerfile": dockerfile, "makefile": makefile, "manifest": manifest},
                temp_dir,
            )

            shutil.rmtree(temp_dir, ignore_errors=True)

            return {
                "success": True,
                "html": html,
                "dockerfile": dockerfile,
                "makefile": makefile,
                "manifest": manifest or {},
                "r4r_log": result.stdout,
            }

        except Exception as e:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            return {"success": False, "error": str(e)}

    def read_file(self, dir_path, filename):
        path = os.path.join(dir_path, filename)
        return open(path).read() if os.path.exists(path) else ""

    def read_json(self, dir_path, filename):
        path = os.path.join(dir_path, filename)
        try:
            return json.load(open(path)) if os.path.exists(path) else {}
        except:
            return {}

    def save_reproducibility_package(self, notebook_id, package, temp_dir):
        repro_dir = f"storage/notebooks/{notebook_id}/reproducibility"
        os.makedirs(repro_dir, exist_ok=True)

        if package["dockerfile"]:
            with open(os.path.join(repro_dir, "Dockerfile"), "w") as f:
                f.write(package["dockerfile"])

        readme = f"""# Reproducibility Package for Notebook {notebook_id}

## Quick Start
cd storage/notebooks/{notebook_id}/reproducibility
docker build -t notebook-{notebook_id} .
docker run --rm -v $(pwd):/workspace notebook-{notebook_id}
"""
        with open(os.path.join(repro_dir, "README.md"), "w") as f:
            f.write(readme)
