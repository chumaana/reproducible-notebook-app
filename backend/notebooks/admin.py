from django.contrib import admin
from .models import Notebook, NotebookBlock, NotebookExecution, ReproducibilityAnalysis


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "is_public", "created_at", "updated_at"]
    list_filter = ["is_public", "created_at", "author"]
    search_fields = ["title", "description", "author__username"]
    readonly_fields = ["id", "created_at", "updated_at"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("id", "title", "author", "description", "is_public")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(NotebookBlock)
class NotebookBlockAdmin(admin.ModelAdmin):
    list_display = ["notebook", "block_type", "order", "execution_status", "updated_at"]
    list_filter = ["block_type", "execution_status", "created_at"]
    search_fields = ["notebook__title", "content"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["notebook", "order"]


@admin.register(NotebookExecution)
class NotebookExecutionAdmin(admin.ModelAdmin):
    list_display = [
        "notebook",
        "status",
        "started_at",
        "completed_at",
        "completed_blocks",
        "failed_blocks",
    ]
    list_filter = ["status", "started_at"]
    search_fields = ["notebook__title"]
    readonly_fields = ["id", "started_at", "completed_at"]


@admin.register(ReproducibilityAnalysis)
class ReproducibilityAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        "notebook",
        "r4r_reproducibility_score",
        "r4r_docker_ready",
        "created_at",
    ]
    list_filter = ["r4r_docker_ready", "has_random_seed", "created_at"]
    search_fields = ["notebook__title"]
    readonly_fields = ["id", "created_at", "updated_at"]
