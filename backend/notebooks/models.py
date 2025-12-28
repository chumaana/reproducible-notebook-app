from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator


class Notebook(models.Model):
    """
    A complete R Markdown document created by a user.
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
    content = models.TextField(blank=True, default="", help_text="R Markdown content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(
        default=False, help_text="Whether this notebook is publicly visible"
    )

    def __str__(self):
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
        return f"{self.notebook.title} - {self.status} - {self.started_at}"

    @property
    def duration(self):
        """Calculate execution duration in seconds"""
        if self.completed_at and self.started_at:
            delta = self.completed_at - self.started_at
            return round(delta.total_seconds(), 2)
        return None


class ReproducibilityAnalysis(models.Model):
    """
    Stores the result of reproducibility analysis for a notebook.
    """

    notebook = models.OneToOneField(
        Notebook,
        on_delete=models.CASCADE,
        related_name="analysis",
        help_text="The notebook being analyzed",
    )

    dependencies = models.JSONField(
        default=list, help_text="List of static analysis issues"
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

    diff_html = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reproducibility Analysis"
        verbose_name_plural = "Reproducibility Analyses"
