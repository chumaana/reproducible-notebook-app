"""
R Package Manager service for detecting and installing R packages.
Handles package resolution from R Markdown content and installation via CRAN.
"""

import subprocess
import re
from typing import List


class RPackageManager:
    """
    Service for managing R package detection and installation.
    Uses Posit Package Manager for reliable package installation.
    """

    def __init__(
        self,
        repo_url: str = "https://packagemanager.posit.co/cran/__linux__/noble/latest",
    ):
        """
        Initialize package manager with CRAN repository URL.

        Args:
            repo_url: CRAN mirror URL for package installation
        """
        self.repo_url = repo_url

    def detect_packages_from_content(self, content: str) -> List[str]:
        """
        Extract list of packages from R markdown content by parsing library() and require() calls.

        Args:
            content: R Markdown content to analyze

        Returns:
            Sorted list of unique package names
        """
        if not content:
            return []

        # Match library() and require() calls
        packages = re.findall(
            r'(?:library|require)\s*\(\s*["\']?([a-zA-Z0-9\.]+)', content
        )
        return sorted(list(set(packages)))

    def install_packages(
        self, packages: List[str], temp_dir: str
    ) -> subprocess.CompletedProcess:
        """
        Install R packages if they don't exist.

        Args:
            packages: List of package names to install
            temp_dir: Working directory for R process

        Returns:
            CompletedProcess with installation results
        """
        if not packages:
            return subprocess.CompletedProcess(
                args=[], returncode=0, stdout="No packages to install", stderr=""
            )

        # Generate R script to check and install packages
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
        """
        Check which packages are already installed in the R environment.

        Args:
            packages: List of package names to check

        Returns:
            List of installed package names
        """
        if not packages:
            return []

        # Generate R script to check package availability
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
