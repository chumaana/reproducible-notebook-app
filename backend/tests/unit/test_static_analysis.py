"""
Unit tests for static code analysis functionality.
Tests reproducibility issue detection in R code.
"""

from django.test import TestCase
from notebooks.static_analyzer import ReproducibilityAnalyzer


class StaticAnalysisTest(TestCase):
    """Test static analysis of R code for reproducibility issues"""

    def setUp(self):
        """Initialize analyzer"""
        self.analyzer = ReproducibilityAnalyzer()

    def test_detect_set_seed_missing(self):
        """Test detection of missing set.seed() for random operations"""
        code_with_random = """
        library(ggplot2)
        x <- rnorm(100)
        y <- runif(50)
        """
        result = self.analyzer.analyze(code_with_random)

        self.assertIn("issues", result)
        # Should detect missing set.seed
        seed_issues = [
            i for i in result["issues"] if "set.seed" in i.get("title", "").lower()
        ]
        self.assertGreater(len(seed_issues), 0)

    def test_detect_absolute_paths(self):
        """Test detection of absolute file paths"""
        code_with_abs_path = """
        data <- read.csv("/home/user/data.csv")
        write.csv(df, "/tmp/output.csv")
        """
        result = self.analyzer.analyze(code_with_abs_path)

        path_issues = [
            i for i in result["issues"] if "path" in i.get("title", "").lower()
        ]
        self.assertGreater(len(path_issues), 0)

    def test_detect_system_calls(self):
        """Test detection of system() calls"""
        code_with_system = """
        system("ls -la")
        system2("wget", "http://example.com/data.csv")
        """
        result = self.analyzer.analyze(code_with_system)

        system_issues = [
            i for i in result["issues"] if "system" in i.get("title", "").lower()
        ]
        self.assertGreater(len(system_issues), 0)

    def test_detect_setwd(self):
        """Test detection of setwd() calls"""
        code_with_setwd = """
        setwd("/home/user/project")
        data <- read.csv("data.csv")
        """
        result = self.analyzer.analyze(code_with_setwd)

        setwd_issues = [
            i for i in result["issues"] if i.get("category") == "environment"
        ]
        self.assertGreater(len(setwd_issues), 0)

    def test_detect_install_packages(self):
        """Test detection of install.packages() calls"""
        code_with_install = """
        install.packages("ggplot2")
        library(dplyr)
        """
        result = self.analyzer.analyze(code_with_install)

        install_issues = [
            i
            for i in result["issues"]
            if "installation" in i.get("category", "").lower()
        ]
        self.assertGreater(len(install_issues), 0)

    def test_clean_code_no_issues(self):
        """Test that clean, reproducible code has minimal issues"""
        clean_code = """
        library(ggplot2)
        set.seed(42)
        data <- data.frame(x = rnorm(100), y = rnorm(100))
        plot(data$x, data$y)
        """
        result = self.analyzer.analyze(clean_code)

        # Should have very few or no critical issues
        high_severity = [i for i in result["issues"] if i.get("severity") == "high"]
        self.assertEqual(len(high_severity), 0)

    def test_issue_line_numbers(self):
        """Test that issues include correct line numbers"""
        code = """
        library(ggplot2)
        x <- rnorm(100)
        setwd("/tmp")
        """
        result = self.analyzer.analyze(code)

        for issue in result["issues"]:
            if "lines" in issue:
                self.assertGreater(len(issue["lines"]), 0)
                for line_info in issue["lines"]:
                    self.assertIn("line_number", line_info)
                    self.assertGreater(line_info["line_number"], 0)

    def test_issue_severity_levels(self):
        """Test that issues have valid severity levels"""
        code = """
        setwd("/tmp")
        x <- rnorm(100)
        system("ls")
        """
        result = self.analyzer.analyze(code)

        valid_severities = ["high", "medium", "low"]
        for issue in result["issues"]:
            self.assertIn(issue.get("severity"), valid_severities)

    def test_issue_fix_suggestions(self):
        """Test that issues include fix suggestions"""
        code = """
        x <- rnorm(100)
        data <- read.csv("/home/user/data.csv")
        """
        result = self.analyzer.analyze(code)

        for issue in result["issues"]:
            self.assertIn("fix", issue)
            self.assertIsInstance(issue["fix"], str)
            self.assertGreater(len(issue["fix"]), 0)

    def test_empty_code_analysis(self):
        """Test analysis of empty code"""
        result = self.analyzer.analyze("")
        self.assertEqual(result["total_issues"], 0)
        self.assertEqual(len(result["issues"]), 0)

    def test_multiline_code_detection(self):
        """Test detection across multiple lines"""
        multiline_code = """
        # Data loading
        data1 <- read.csv("/path/to/file1.csv")
        data2 <- read.csv("/path/to/file2.csv")
        
        # Random generation
        x <- rnorm(100)
        y <- runif(50)
        z <- sample(1:100, 20)
        """
        result = self.analyzer.analyze(multiline_code)

        # Should detect multiple issues
        self.assertGreater(result["total_issues"], 2)

    def test_code_with_comments(self):
        """Test that comments don't trigger false positives"""
        code_with_comments = """
        # Don't use setwd() in production
        # system() calls are dangerous
        library(ggplot2)
        set.seed(42)
        x <- rnorm(100)
        """
        result = self.analyzer.analyze(code_with_comments)

        # Comments should not trigger issues
        setwd_in_comment = [
            i for i in result["issues"] if "setwd" in i.get("title", "").lower()
        ]
        self.assertEqual(len(setwd_in_comment), 0)
