"""
Static analysis tool for detecting reproducibility issues in R Markdown code.
"""

import re
from typing import List, Dict


class ReproducibilityAnalyzer:
    """
    Analyzes R Markdown content for reproducibility issues.

    Detects common problems that affect reproducibility including randomness
    without seeds, absolute paths, time-dependent code, and security issues.
    """

    def analyze(self, rmd_content: str) -> Dict:
        """
        Perform static analysis on R Markdown content.

        Args:
            rmd_content: R Markdown source code as string.

        Returns:
            Dictionary containing:
                - issues: List of detected issues with severity and line numbers.
                - total_issues: Total count of issue occurrences.
        """
        lines = rmd_content.split("\n")
        issues = []

        # Check for random functions without seed
        random_issues = self._detect_random_with_lines(lines)
        has_seed = any("set.seed" in line for line in lines)
        if random_issues and not has_seed:
            issues.append(
                {
                    "category": "randomness",
                    "severity": "high",
                    "title": "Missing set.seed()",
                    "details": "Random functions detected without a seed.",
                    "fix": "Add set.seed(123) at the start.",
                    "lines": random_issues,
                }
            )

        # Check for time-dependent code
        timestamp_lines = self._find_pattern_lines(lines, r"Sys\.(time|Date|timezone)")
        if timestamp_lines:
            issues.append(
                {
                    "category": "timestamp",
                    "severity": "medium",
                    "title": "Time-dependent code",
                    "details": "Uses current system time/date.",
                    "fix": "Use fixed dates or pass date as a parameter.",
                    "lines": timestamp_lines,
                }
            )

        # Check for absolute file paths
        path_lines = self._find_absolute_paths(lines)
        if path_lines:
            issues.append(
                {
                    "category": "paths",
                    "severity": "high",
                    "title": "Absolute file paths",
                    "details": "Hard-coded system paths won't work on other machines.",
                    "fix": "Use relative paths or the 'here' package.",
                    "lines": path_lines,
                }
            )

        # Check for external data downloads
        download_lines = self._find_pattern_lines(lines, r"download\.file|url\(")
        if download_lines:
            issues.append(
                {
                    "category": "external_data",
                    "severity": "medium",
                    "title": "External data sources",
                    "details": "Downloads data from URLs which might break.",
                    "fix": "Include data in the repo or use versioned URLs.",
                    "lines": download_lines,
                }
            )

        # Check for install.packages()
        install_lines = self._find_pattern_lines(lines, r"install\.packages\s*\(")
        if install_lines:
            issues.append(
                {
                    "category": "installation",
                    "severity": "high",
                    "title": "Hardcoded Package Install",
                    "details": "Scripts should not install packages directly.",
                    "fix": "Remove install.packages(). Rely on Docker/renv.",
                    "lines": install_lines,
                }
            )

        # Check for setwd()
        setwd_lines = self._find_pattern_lines(lines, r"setwd\s*\(")
        if setwd_lines:
            issues.append(
                {
                    "category": "environment",
                    "severity": "high",
                    "title": "Changing Working Directory",
                    "details": "setwd() breaks reproducibility on other computers.",
                    "fix": "Use relative paths or project roots.",
                    "lines": setwd_lines,
                }
            )

        # Check for interactive commands
        interactive_lines = self._find_pattern_lines(
            lines, r"\b(View|browser|edit|file\.choose)\s*\("
        )
        if interactive_lines:
            issues.append(
                {
                    "category": "interactive",
                    "severity": "high",
                    "title": "Interactive Command Detected",
                    "details": "Commands like View() stop execution in Docker.",
                    "fix": "Remove interactive commands.",
                    "lines": interactive_lines,
                }
            )

        # Check for hardcoded secrets
        secret_lines = self._find_secrets(lines)
        if secret_lines:
            issues.append(
                {
                    "category": "security",
                    "severity": "critical",
                    "title": "Potential API Key / Secret",
                    "details": "Hardcoded secrets are a security risk.",
                    "fix": "Use environment variables: Sys.getenv('MY_KEY').",
                    "lines": secret_lines,
                }
            )

        return {
            "issues": issues,
            "total_issues": sum(len(i["lines"]) for i in issues),
        }

    def _detect_random_with_lines(self, lines: List[str]) -> List[Dict]:
        """
        Detect random number generation functions.

        Args:
            lines: List of code lines.

        Returns:
            List of dictionaries with line_number and code for each occurrence.
        """
        random_patterns = [
            (r"\bsample\s*\(", "sample()"),
            (r"\brnorm\s*\(", "rnorm()"),
            (r"\brunif\s*\(", "runif()"),
            (r"\brbinom\s*\(", "rbinom()"),
            (r"\bsample_n\s*\(", "sample_n()"),
        ]
        found = []
        for line_num, line in enumerate(lines, start=1):
            if line.strip().startswith("#"):
                continue
            for pattern, func_name in random_patterns:
                if re.search(pattern, line):
                    found.append({"line_number": line_num - 6, "code": line.strip()})
        return found

    def _find_pattern_lines(self, lines: List[str], pattern: str) -> List[Dict]:
        """
        Find lines matching a regex pattern.

        Args:
            lines: List of code lines.
            pattern: Regular expression pattern to search for.

        Returns:
            List of dictionaries with line_number and code for each match.
        """
        found = []
        for line_num, line in enumerate(lines, start=1):
            if line.strip().startswith("#"):
                continue
            if re.search(pattern, line):
                found.append({"line_number": line_num - 6, "code": line.strip()})
        return found

    def _find_absolute_paths(self, lines: List[str]) -> List[Dict]:
        """
        Detect absolute file paths in code.

        Args:
            lines: List of code lines.

        Returns:
            List of dictionaries with line_number, code, and matched path.
        """
        found = []
        path_pattern = r'["\'](?:[a-zA-Z]:[\\/]|[\\/])[^"\']+["\']'

        for line_num, line in enumerate(lines, start=1):
            if line.strip().startswith("#"):
                continue

            # Skip library/require statements
            if "library(" in line or "require(" in line:
                continue

            matches = re.findall(path_pattern, line)
            for match in matches:
                # Skip URLs
                if "://" in match or "http" in match:
                    continue
                found.append(
                    {"line_number": line_num - 6, "code": line.strip(), "match": match}
                )
        return found

    def _find_secrets(self, lines: List[str]) -> List[Dict]:
        """
        Detect potential hardcoded API keys and secrets.

        Args:
            lines: List of code lines.

        Returns:
            List of dictionaries with line_number and masked code.
        """
        found = []
        patterns = [
            r"sk_live_[0-9a-zA-Z]{20,}",
            r"(?:api_key|access_token|secret)\s*=\s*['\"][a-zA-Z0-9_\-]{20,}['\"]",
        ]

        for line_num, line in enumerate(lines, start=1):
            if line.strip().startswith("#"):
                continue
            for p in patterns:
                if re.search(p, line):
                    masked_code = re.sub(p, "***SECRET***", line.strip())
                    found.append({"line_number": line_num - 6, "code": masked_code})
        return found
