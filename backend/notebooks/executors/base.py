"""
Base executor class providing common utilities for all notebook executors.
Includes command execution, logging, and error handling functionality.
"""

import subprocess
import datetime
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class BaseExecutor(ABC):
    """
    Abstract base class for all executor implementations.
    Provides shared utilities for command execution, logging, and error responses.
    """

    def __init__(self):
        self.logger_name = self.__class__.__name__

    def _run_command(
        self,
        cmd: list,
        cwd: str,
        desc: str = "Command",
        env: Optional[Dict[str, str]] = None,
        timeout: int = 600,
    ) -> subprocess.CompletedProcess:
        """
        Execute a shell command with logging and error handling.

        Args:
            cmd: Command and arguments as list
            cwd: Working directory for command execution
            desc: Description for logging
            env: Environment variables
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess object with stdout, stderr, and returncode
        """
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

    def _log(self, msg: str, level: str = "INFO"):
        """Log message with timestamp and logger name."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] [{self.logger_name}] {msg}", flush=True)

    def _log_header(self, msg: str):
        """Log major section header."""
        print(f"\n== {msg} ==", flush=True)

    def _log_section(self, msg: str):
        """Log minor section header."""
        print(f"\n--- {msg} ---", flush=True)

    def _error_response(
        self,
        msg: str,
        detail: str,
        html: str = "",
        static_analysis: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Create standardized error response dictionary.

        Args:
            msg: Error message summary
            detail: Detailed error information
            html: HTML output (if any)
            static_analysis: Static analysis results

        Returns:
            Dictionary with error information
        """
        return {
            "success": False,
            "error": f"{msg}:\n{detail}",
            "html": html,
            "static_analysis": static_analysis or {},
        }

    @abstractmethod
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Main execution method - must be implemented by subclasses.

        Returns:
            Dictionary containing execution results with keys:
                - success: bool
                - html: str (on success)
                - error: str (on failure)
                - static_analysis: dict (optional)
        """
        pass
