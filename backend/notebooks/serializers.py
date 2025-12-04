from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notebook, ReproducibilityAnalysis, Execution


class UserSerializer(serializers.ModelSerializer):
    """For user registration, profiles, and management"""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id"]


class NotebookSerializer(serializers.ModelSerializer):
    """Main serializer for notebooks"""

    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Notebook
        fields = [
            "id",
            "title",
            "author",
            "content",
            "created_at",
            "updated_at",
            "is_public",
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        user = (
            request.user
            if request and request.user.is_authenticated
            else User.objects.first()
        )

        if not user:
            user = User.objects.create_user(
                username="default_user",
                email="default@example.com",
                password="default123",
            )

        validated_data["author"] = user
        return super().create(validated_data)


class ExecutionSerializer(serializers.ModelSerializer):
    """Track execution history"""

    class Meta:
        model = Execution
        fields = [
            "id",
            "notebook",
            "html_output",
            "status",
            "started_at",
            "completed_at",
            "error_message",
        ]
        read_only_fields = ["id", "started_at"]


class ReproducibilityAnalysisSerializer(serializers.ModelSerializer):
    """R4R analysis results"""

    class Meta:
        model = ReproducibilityAnalysis
        fields = [
            "id",
            "notebook",
            "r4r_score",
            "dependencies",
            "system_deps",
            "dockerfile",
            "makefile",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
