import uuid
from django.db import models
from django.contrib.auth.models import User


class Notebook(models.Model):
    """A complete R Markdown document"""

    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # Single field for entire R Markdown content
    content = models.TextField(blank=True, default="")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Execution(models.Model):
    """Record of notebook execution"""

    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE)

    # Output from rendering
    html_output = models.TextField()
    status = models.CharField(max_length=20)  # 'running', 'completed', 'failed'

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    error_message = models.TextField(blank=True)


class NotebookExecution(models.Model):
    EXECUTION_STATUS = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    notebook = models.ForeignKey(
        Notebook, on_delete=models.CASCADE, related_name="executions"
    )
    status = models.CharField(
        max_length=20, choices=EXECUTION_STATUS, default="pending"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_blocks = models.PositiveIntegerField(default=0)
    completed_blocks = models.PositiveIntegerField(default=0)
    failed_blocks = models.PositiveIntegerField(default=0)
    error_log = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.notebook.title} - {self.status} - {self.started_at}"


class ReproducibilityAnalysis(models.Model):
    notebook = models.OneToOneField(
        Notebook, on_delete=models.CASCADE, related_name="analysis"
    )
    r4r_score = models.IntegerField(default=0)
    dependencies = models.JSONField(default=list)
    system_deps = models.JSONField(default=list)
    dockerfile = models.TextField(blank=True, default="")
    makefile = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
