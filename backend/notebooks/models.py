"""
Django models for the Reproducible Notebook Application.
Defines Notebook, Execution, and ReproducibilityAnalysis models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator


class Notebook(models.Model):
    """
    R Markdown document with metadata and relationships.

    Attributes:
        title: Notebook title (3-200 characters).
        author: User who created this notebook.
        content: Full R Markdown source code.
        created_at: Timestamp when notebook was created.
        updated_at: Timestamp of last modification.
        is_public: Whether notebook is publicly visible.
    """

    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3, "Title must be at least 3 characters")],
        help_text="Notebook title (3-200 characters)",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notebooks",
        help_text="User who created this notebook",
    )
    content = models.TextField(default="", help_text="R Markdown content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(
        default=False, help_text="Whether this notebook is publicly visible"
    )

    def __str__(self):
        """Return string representation of notebook."""
        return f"{self.title} ({self.author.username})"

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Notebook"
        verbose_name_plural = "Notebooks"
        indexes = [
            models.Index(fields=["-updated_at"]),
            models.Index(fields=["author", "-updated_at"]),
        ]


class Execution(models.Model):
    """
    Record of a single notebook execution.

    Attributes:
        notebook: The notebook that was executed.
        status: Current execution status (pending/running/completed/failed).
        html_output: Generated HTML output from R Markdown rendering.
        error_message: Error message if execution failed.
        started_at: When execution began.
        completed_at: When execution finished (None if still running).
    """

    EXECUTION_STATUS = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    notebook = models.ForeignKey(
        Notebook,
        on_delete=models.CASCADE,
        related_name="executions",
        help_text="The notebook that was executed",
    )
    status = models.CharField(
        max_length=20,
        choices=EXECUTION_STATUS,
        default="pending",
        help_text="Current execution status",
    )
    html_output = models.TextField(
        blank=True, help_text="Generated HTML output from R Markdown rendering"
    )
    error_message = models.TextField(
        blank=True, help_text="Error message if execution failed"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Execution"
        verbose_name_plural = "Executions"
        indexes = [
            models.Index(fields=["notebook", "-started_at"]),
        ]

    def __str__(self):
        """Return string representation of execution."""
        return f"{self.notebook.title} - {self.status} - {self.started_at}"

    @property
    def duration(self):
        """
        Calculate execution duration in seconds.

        Returns:
            float: Duration in seconds rounded to 2 decimals, or None if not completed.
        """
        if self.completed_at and self.started_at:
            delta = self.completed_at - self.started_at
            return round(delta.total_seconds(), 2)
        return None


class ReproducibilityAnalysis(models.Model):
    """
    Reproducibility analysis results for a notebook.

    Attributes:
        notebook: The notebook being analyzed (one-to-one).
        dependencies: List of R package dependencies detected.
        system_deps: List of system-level dependencies.
        dockerfile: Generated Dockerfile content.
        makefile: Generated Makefile content.
        diff_html: HTML diff visualization from rdiff.
        r4r_data: Runtime metrics from r4r tool.
        created_at: When analysis was created.
        updated_at: When analysis was last updated.
    """

    notebook = models.OneToOneField(
        Notebook,
        on_delete=models.CASCADE,
        related_name="analysis",
        help_text="The notebook being analyzed",
    )
    dependencies = models.JSONField(
        default=list, help_text="List of R package dependencies"
    )
    system_deps = models.JSONField(
        default=list, help_text="List of system-level dependencies"
    )
    dockerfile = models.TextField(
        blank=True, default="", help_text="Generated Dockerfile content"
    )
    makefile = models.TextField(
        blank=True, default="", help_text="Generated Makefile content"
    )
    diff_html = models.TextField(
        blank=True, null=True, help_text="HTML diff visualization from rdiff"
    )
    r4r_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="r4r metrics: r_packages, system_libs, files_accessed",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reproducibility Analysis"
        verbose_name_plural = "Reproducibility Analyses"

    def __str__(self):
        """Return string representation of analysis."""
        return f"Analysis for {self.notebook.title}"
