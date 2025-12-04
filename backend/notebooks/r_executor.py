import subprocess
import tempfile
import os
import shutil
import json


class RExecutor:
    """Execute R Markdown using r4r tool"""

    def execute_rmd(self, content, notebook_id):
        """Execute with r4r - it does everything"""

        try:
            # Create temp directory
            temp_dir = tempfile.mkdtemp()
            rmd_path = os.path.join(temp_dir, "notebook.Rmd")
            output_dir = os.path.join(temp_dir, "output")
            result_file = "notebook.html"

            # Write notebook
            with open(rmd_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"DEBUG: Running r4r on {rmd_path}")
            print(f"DEBUG: Output dir: {output_dir}")

            # Run r4r - OPTIONS MUST COME BEFORE COMMAND!
            result = subprocess.run(
                [
                    "r4r",
                    "--output",
                    output_dir,
                    "--result",
                    result_file,
                    "--docker-image-tag",
                    f"notebook-{notebook_id}",
                    "--docker-container-name",
                    f"notebook-container-{notebook_id}",
                    "--skip-make",
                    "R",
                    "-e",
                    f'rmarkdown::render("{rmd_path}")',
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            print(f"r4r stdout: {result.stdout}")
            print(f"r4r stderr: {result.stderr}")

            print(f"\n=== DEBUG: Checking r4r output ===")
            print(f"Temp dir contents: {os.listdir(temp_dir)}")
            if os.path.exists(output_dir):
                print(f"Output dir contents: {os.listdir(output_dir)}")
                for item in os.listdir(output_dir):
                    item_path = os.path.join(output_dir, item)
                    if os.path.isdir(item_path):
                        print(f"  Subdir {item}: {os.listdir(item_path)}")
            else:
                print(f"Output dir does not exist: {output_dir}")

            # Read HTML result (r4r may put it in different locations)
            html_path = None
            possible_paths = [
                os.path.join(output_dir, "result", result_file),
                os.path.join(temp_dir, result_file),
                rmd_path.replace(".Rmd", ".html"),
                os.path.join(output_dir, result_file),
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    html_path = path
                    print(f"DEBUG: Found HTML at {html_path}")
                    break

            if not html_path:
                return {
                    "success": False,
                    "error": f"No HTML output found. r4r stderr: {result.stderr}",
                }

            # Read HTML
            with open(html_path, "r", encoding="utf-8") as f:
                html = f.read()

            # Read generated Dockerfile
            dockerfile_path = os.path.join(output_dir, "Dockerfile")
            dockerfile = ""
            if os.path.exists(dockerfile_path):
                with open(dockerfile_path, "r") as f:
                    dockerfile = f.read()
                print(f"DEBUG: Found Dockerfile, length: {len(dockerfile)}")
            else:
                print(f"DEBUG: No Dockerfile found at {dockerfile_path}")

            # Read Makefile
            makefile = self.read_makefile(output_dir)
            if makefile:
                print(f"DEBUG: Found Makefile, length: {len(makefile)}")

            # Extract dependencies from r4r output
            dependencies = self.extract_dependencies_from_output(output_dir)
            print(f"DEBUG: Found dependencies: {dependencies}")

            print(
                f"DEBUG: Successfully processed. HTML length: {len(html)}, Dockerfile length: {len(dockerfile)}"
            )

            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)

            # Return results
            return {
                "success": True,
                "html": html,
                "dockerfile": dockerfile,
                "makefile": makefile,
                "dependencies": dependencies,
                "system_deps": [],
            }

        except subprocess.TimeoutExpired:
            if "temp_dir" in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            return {"success": False, "error": "r4r execution timeout (>120s)"}

        except Exception as e:
            if "temp_dir" in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            return {"success": False, "error": f"r4r execution failed: {str(e)}"}

    def extract_dependencies_from_output(self, output_dir):
        """Extract dependencies from r4r output files"""
        deps = []

        if not os.path.exists(output_dir):
            return deps

        # r4r may create manifest or package list files
        manifest_file = os.path.join(output_dir, "manifest.json")
        if os.path.exists(manifest_file):
            try:
                with open(manifest_file, "r") as f:
                    data = json.load(f)
                    deps = data.get("r_packages", [])
            except Exception as e:
                print(f"DEBUG: Failed to read manifest: {e}")

        # Check for other r4r output files
        try:
            for filename in os.listdir(output_dir):
                if filename.endswith(".txt") and "package" in filename.lower():
                    try:
                        filepath = os.path.join(output_dir, filename)
                        with open(filepath, "r") as f:
                            content = f.read()
                            # Parse package names
                            import re

                            packages = re.findall(r"[\w.]+", content)
                            deps.extend(packages)
                    except:
                        pass
        except Exception as e:
            print(f"DEBUG: Failed to scan output_dir: {e}")

        return list(set(deps))  # Remove duplicates

    def read_makefile(self, output_dir):
        """Read r4r-generated Makefile"""
        makefile_path = os.path.join(output_dir, "Makefile")
        if os.path.exists(makefile_path):
            try:
                with open(makefile_path, "r") as f:
                    return f.read()
            except Exception as e:
                print(f"DEBUG: Failed to read Makefile: {e}")
        return ""
