import uuid
from django.db import models
from django.contrib.auth.models import User


class Notebook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, default="Untitled Notebook")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notebooks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-updated_at"]


class NotebookBlock(models.Model):
    BLOCK_TYPES = [
        ("code", "Code Block"),
        ("markdown", "Markdown Block"),
    ]

    EXECUTION_STATUS = [
        ("idle", "Idle"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notebook = models.ForeignKey(
        Notebook, on_delete=models.CASCADE, related_name="blocks"
    )
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES, default="code")
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    output = models.TextField(blank=True)
    error_output = models.TextField(blank=True)
    execution_status = models.CharField(
        max_length=20, choices=EXECUTION_STATUS, default="idle"
    )
    execution_time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.notebook.title} - {self.block_type} - {self.order}"


class NotebookExecution(models.Model):
    EXECUTION_STATUS = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notebook = models.ForeignKey(
        Notebook, on_delete=models.CASCADE, related_name="analyses"
    )
    has_random_seed = models.BooleanField(default=False)
    has_hardcoded_paths = models.BooleanField(default=False)
    has_external_deps = models.BooleanField(default=False)
    has_time_deps = models.BooleanField(default=False)
    has_interactive_input = models.BooleanField(default=False)

    # R4R analysis results
    r4r_dependencies = models.JSONField(default=list, blank=True)
    r4r_system_packages = models.JSONField(default=list, blank=True)
    r4r_docker_ready = models.BooleanField(default=False)
    r4r_reproducibility_score = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Reproducibility Analyses"

    def __str__(self):
        return f"{self.notebook.title} - Analysis - {self.created_at}"
