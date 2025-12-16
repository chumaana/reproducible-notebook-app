import re
from typing import List, Dict, Tuple


class ReproducibilityAnalyzer:

    def analyze(self, rmd_content: str) -> Dict:
        """Static analysis з line numbers"""
        lines = rmd_content.split("\n")
        issues = []

        # 1. Random functions without set.seed()
        random_issues = self._detect_random_with_lines(lines)
        has_seed = any("set.seed" in line for line in lines)
        if random_issues and not has_seed:
            issues.append(
                {
                    "category": "randomness",
                    "severity": "high",
                    "title": "Missing set.seed()",
                    "details": f"Random functions without reproducible seed",
                    "fix": "Add set.seed(123) at the start of your R chunk",
                    "lines": random_issues,  # 🔥 Line numbers!
                }
            )

        # 2. Timestamps
        timestamp_lines = self._find_pattern_lines(lines, r"Sys\.(time|Date|timezone)")
        if timestamp_lines:
            issues.append(
                {
                    "category": "timestamp",
                    "severity": "medium",
                    "title": "Time-dependent code",
                    "details": "Uses current system time/date",
                    "fix": "Use fixed dates: date <- as.Date('2025-12-10')",
                    "lines": timestamp_lines,
                }
            )

        # 3. Absolute paths
        path_lines = self._find_absolute_paths(lines)
        if path_lines:
            issues.append(
                {
                    "category": "paths",
                    "severity": "high",
                    "title": "Absolute file paths",
                    "details": "Hard-coded system paths",
                    "fix": "Use relative paths or here::here()",
                    "lines": path_lines,
                }
            )

        # 4. External downloads
        download_lines = self._find_pattern_lines(lines, r"download\.file|url\(")
        if download_lines:
            issues.append(
                {
                    "category": "external_data",
                    "severity": "medium",
                    "title": "External data sources",
                    "details": "Downloads data from URLs",
                    "fix": "Pin data versions or include checksums",
                    "lines": download_lines,
                }
            )

        return {
            "issues": issues,
            "code_lines": lines,
            "total_lines": len(lines),
        }

    def _detect_random_with_lines(self, lines: List[str]) -> List[Dict]:
        """Detect random functions з line numbers"""
        random_patterns = [
            (r"\bsample\s*\(", "sample()"),
            (r"\brnorm\s*\(", "rnorm()"),
            (r"\brunif\s*\(", "runif()"),
            (r"\brbinom\s*\(", "rbinom()"),
            (r"\bsample_n\s*\(", "sample_n()"),
        ]

        found = []
        for line_num, line in enumerate(lines, start=1):
            for pattern, func_name in random_patterns:
                if re.search(pattern, line):
                    found.append(
                        {
                            "line_number": line_num,
                            "code": line.strip(),
                            "function": func_name,
                        }
                    )
        return found

    def _find_pattern_lines(self, lines: List[str], pattern: str) -> List[Dict]:
        """Generic pattern finder з line numbers"""
        found = []
        for line_num, line in enumerate(lines, start=1):
            if re.search(pattern, line):
                found.append({"line_number": line_num, "code": line.strip()})
        return found

    def _find_absolute_paths(self, lines: List[str]) -> List[Dict]:
        """Find absolute paths з line numbers"""
        found = []
        path_pattern = r'["\']([/\\][A-Za-z]:?[^\s"\']+)["\']'

        for line_num, line in enumerate(lines, start=1):
            matches = re.findall(path_pattern, line)
            if matches:
                found.append(
                    {"line_number": line_num, "code": line.strip(), "paths": matches}
                )
        return found
