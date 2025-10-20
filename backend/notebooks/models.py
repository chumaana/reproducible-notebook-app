import uuid
from django.db import models
from django.contrib.auth.models import User


class Notebook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, default="Untitled Notebook")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-updated_at"]


class NotebookBlock(models.Model):
    BLOCK_TYPES = [
        ("code", "Code Block"),
        ("markdown", "Markdown Block"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notebook = models.ForeignKey(
        Notebook, on_delete=models.CASCADE, related_name="blocks"
    )
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES, default="code")
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    output = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.notebook.title} - {self.block_type} - {self.order}"
