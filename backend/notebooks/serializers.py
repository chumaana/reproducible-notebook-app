from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notebook, NotebookBlock, NotebookExecution, ReproducibilityAnalysis


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id"]


class NotebookBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotebookBlock
        fields = [
            "id",
            "block_type",
            "content",
            "order",
            "output",
            "error_output",
            "execution_status",
            "execution_time",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class NotebookListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing notebooks"""

    author = serializers.StringRelatedField(read_only=True)
    block_count = serializers.SerializerMethodField()

    class Meta:
        model = Notebook
        fields = [
            "id",
            "title",
            "author",
            "description",
            "is_public",
            "block_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at"]

    def get_block_count(self, obj):
        return obj.blocks.count()


class NotebookDetailSerializer(serializers.ModelSerializer):
    """Full serializer with blocks"""

    blocks = NotebookBlockSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Notebook
        fields = [
            "id",
            "title",
            "author",
            "description",
            "blocks",
            "is_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at"]

    def create(self, validated_data):
        # Get user from request context
        request = self.context.get("request")
        user = None

        if request and hasattr(request, "user"):
            if request.user.is_authenticated:
                user = request.user

        # If no authenticated user, use the first user (for development)
        if not user:
            from django.contrib.auth.models import User

            user = User.objects.first()

            # If no users exist at all, create one
            if not user:
                user = User.objects.create_user(
                    username="default_user",
                    email="default@example.com",
                    password="default123",
                )

        validated_data["author"] = user
        return super().create(validated_data)


class NotebookExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotebookExecution
        fields = [
            "id",
            "notebook",
            "status",
            "started_at",
            "completed_at",
            "total_blocks",
            "completed_blocks",
            "failed_blocks",
            "error_log",
        ]
        read_only_fields = ["id", "started_at"]


class ReproducibilityAnalysisSerializer(serializers.ModelSerializer):
    checks = serializers.SerializerMethodField()

    class Meta:
        model = ReproducibilityAnalysis
        fields = [
            "id",
            "notebook",
            "has_random_seed",
            "has_hardcoded_paths",
            "has_external_deps",
            "has_time_deps",
            "has_interactive_input",
            "r4r_dependencies",
            "r4r_system_packages",
            "r4r_docker_ready",
            "r4r_reproducibility_score",
            "checks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_checks(self, obj):
        """Format checks for frontend display"""
        checks = []

        checks.append(
            {
                "name": "Random Seed",
                "status": "ok" if obj.has_random_seed else "warning",
                "message": (
                    "Random seed is set"
                    if obj.has_random_seed
                    else "No random seed detected"
                ),
            }
        )

        checks.append(
            {
                "name": "Hardcoded Paths",
                "status": "warning" if obj.has_hardcoded_paths else "ok",
                "message": (
                    "Hardcoded paths detected"
                    if obj.has_hardcoded_paths
                    else "No hardcoded paths"
                ),
            }
        )

        checks.append(
            {
                "name": "External Dependencies",
                "status": "warning" if obj.has_external_deps else "ok",
                "message": (
                    "External dependencies detected"
                    if obj.has_external_deps
                    else "No external dependencies"
                ),
            }
        )

        checks.append(
            {
                "name": "Time Dependencies",
                "status": "warning" if obj.has_time_deps else "ok",
                "message": (
                    "Time-dependent code detected"
                    if obj.has_time_deps
                    else "No time dependencies"
                ),
            }
        )

        return checks
