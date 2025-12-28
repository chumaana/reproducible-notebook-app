# notebooks/services/package_manager.py
import subprocess
import re
from typing import List


class RPackageManager:
    """Service for managing R packages"""

    def __init__(
        self,
        repo_url: str = "https://packagemanager.posit.co/cran/__linux__/noble/latest",
    ):
        self.repo_url = repo_url

    def detect_packages_from_content(self, content: str) -> List[str]:
        """Extract list of packages from R markdown content"""
        if not content:
            return []

        packages = re.findall(
            r'(?:library|require)\s*\(\s*["\']?([a-zA-Z0-9\.]+)', content
        )
        return sorted(list(set(packages)))

    def install_packages(
        self, packages: List[str], temp_dir: str
    ) -> subprocess.CompletedProcess:
        """Install R packages if they don't exist"""
        if not packages:
            return subprocess.CompletedProcess(
                args=[], returncode=0, stdout="No packages to install", stderr=""
            )

        install_script = f"""
        pkgs <- c('{ "', '".join(packages) }')
        repo <- '{self.repo_url}'
        
        for (pkg in pkgs) {{
            if (!require(pkg, character.only = TRUE, quietly = TRUE)) {{
                message(paste("Installing missing package:", pkg))
                install.packages(pkg, repos = repo)
            }} else {{
                message(paste("Package already installed:", pkg))
            }}
        }}
        """

        result = subprocess.run(
            ["R", "-e", install_script],
            cwd=temp_dir,
            capture_output=True,
            text=True,
        )

        return result

    def check_installed(self, packages: List[str]) -> List[str]:
        """Check which packages are already installed"""
        if not packages:
            return []

        check_script = f"""
        pkgs <- c({", ".join([f"'{p}'" for p in packages])})
        installed <- pkgs[sapply(pkgs, function(p) requireNamespace(p, quietly = TRUE))]
        cat(paste(installed, collapse=","))
        """

        result = subprocess.run(
            ["R", "-e", check_script],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0 and result.stdout:
            return result.stdout.strip().split(",")

        return []
