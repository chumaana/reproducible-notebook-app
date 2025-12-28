from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notebook, ReproducibilityAnalysis, Execution


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with password hashing and notebook count.
    Used for registration and profile management.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={"input_type": "password"},
        help_text="Password must be at least 8 characters",
    )
    notebook_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "notebook_count",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]

    def get_notebook_count(self, obj):
        """Return number of notebooks user created"""
        return obj.notebooks.count()

    def validate_username(self, value):
        """Ensure username is alphanumeric"""
        if not value.replace("_", "").replace("-", "").isalnum():
            raise serializers.ValidationError(
                "Username must contain only letters, numbers, hyphens and underscores"
            )
        return value

    def validate_email(self, value):
        """Ensure email is not already taken"""
        if self.instance and self.instance.email == value:
            return value
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use")
        return value

    def create(self, validated_data):
        """Create user with hashed password"""
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class ReproducibilityAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer for ReproducibilityAnalysis model.
    Includes computed fields like warning count.
    """

    notebook_title = serializers.CharField(source="notebook.title", read_only=True)
    warning_count = serializers.SerializerMethodField(read_only=True)
    is_reproducible = serializers.BooleanField(read_only=True)

    class Meta:
        model = ReproducibilityAnalysis
        fields = [
            "id",
            "notebook",
            "notebook_title",
            "r4r_score",
            "dependencies",
            "system_deps",
            "dockerfile",
            "makefile",
            "warnings",
            "warning_count",
            "docker_image_tag",
            "is_reproducible",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_reproducible"]

    def get_warning_count(self, obj):
        """Return number of warnings"""
        return len(obj.warnings) if obj.warnings else 0


class ExecutionSerializer(serializers.ModelSerializer):
    """
    Serializer for Execution model.
    Includes computed duration field.
    """

    notebook_title = serializers.CharField(source="notebook.title", read_only=True)
    duration_seconds = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Execution
        fields = [
            "id",
            "notebook",
            "notebook_title",
            "status",
            "html_output",
            "error_message",
            "duration_seconds",
            "started_at",
            "completed_at",
        ]
        read_only_fields = ["id", "started_at"]

    def get_duration_seconds(self, obj):
        """Calculate execution duration"""
        return obj.duration


class NotebookSerializer(serializers.ModelSerializer):
    """
    Full serializer for Notebook model.
    Includes nested analysis and computed fields.
    """

    author = serializers.ReadOnlyField(source="author.username")
    author_id = serializers.ReadOnlyField(source="author.id")

    analysis = ReproducibilityAnalysisSerializer(read_only=True)

    execution_count = serializers.SerializerMethodField(read_only=True)
    last_execution_status = serializers.SerializerMethodField(read_only=True)
    has_analysis = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Notebook
        fields = [
            "id",
            "title",
            "author",
            "author_id",
            "content",
            "created_at",
            "updated_at",
            "is_public",
            "analysis",
            "execution_count",
            "last_execution_status",
            "has_analysis",
        ]
        read_only_fields = [
            "id",
            "author",
            "author_id",
            "created_at",
            "updated_at",
            "analysis",
        ]

    def get_execution_count(self, obj):
        """Return number of executions"""
        return obj.executions.count()

    def get_last_execution_status(self, obj):
        """Return status of most recent execution"""
        last_execution = obj.executions.first()
        return last_execution.status if last_execution else None

    def get_has_analysis(self, obj):
        """Check if notebook has reproducibility analysis"""
        return hasattr(obj, "analysis")

    def validate_title(self, value):
        """Ensure title is not empty or whitespace only"""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()

    def validate_content(self, value):
        """Basic R markdown validation"""
        if value and len(value) > 10:
            # Check if content looks like R markdown
            r_indicators = ["``````r", "library(", "require("]
            if not any(indicator in value for indicator in r_indicators):
                # Warning but don't block
                pass
        return value


class NotebookListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for notebook lists (without content).
    Optimized for list views with minimal data transfer.
    """

    author = serializers.ReadOnlyField(source="author.username")
    execution_count = serializers.SerializerMethodField(read_only=True)
    has_analysis = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Notebook
        fields = [
            "id",
            "title",
            "author",
            "created_at",
            "updated_at",
            "is_public",
            "execution_count",
            "has_analysis",
        ]

    def get_execution_count(self, obj):
        """Return number of executions"""
        return obj.executions.count()

    def get_has_analysis(self, obj):
        """Check if notebook has reproducibility analysis"""
        return hasattr(obj, "analysis")
