from django.contrib import admin
from .models import Notebook, Execution, ReproducibilityAnalysis


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "created_at", "updated_at", "is_public"]
    list_filter = ["is_public", "created_at"]
    search_fields = ["title", "author__username"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin):
    list_display = ["notebook", "status", "started_at", "completed_at"]
    list_filter = ["status", "started_at"]
    readonly_fields = ["started_at", "completed_at"]


@admin.register(ReproducibilityAnalysis)
class ReproducibilityAnalysisAdmin(admin.ModelAdmin):
    list_display = ["notebook", "r4r_score", "created_at"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at", "updated_at"]
