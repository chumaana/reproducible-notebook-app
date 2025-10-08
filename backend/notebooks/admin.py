from django.contrib import admin
from .models import Notebook


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "created_at", "updated_at"]
    list_filter = ["created_at", "author"]
    search_fields = ["title", "content"]
