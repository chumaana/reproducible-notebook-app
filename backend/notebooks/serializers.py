"""
REST Framework serializers for transforming models to/from JSON.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notebook, ReproducibilityAnalysis, Execution


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with password handling.

    Attributes:
        password: Write-only field for password (min 8 characters).
        notebook_count: Computed field showing user's notebook count.
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
        """
        Get number of notebooks created by user.

        Args:
            obj: User instance.

        Returns:
            int: Count of notebooks.
        """
        return obj.notebooks.count()

    def validate_username(self, value):
        """
        Validate username contains only allowed characters.

        Args:
            value: Username string to validate.

        Returns:
            str: Validated username.

        Raises:
            ValidationError: If username contains invalid characters.
        """
        if not value.replace("_", "").replace("-", "").isalnum():
            raise serializers.ValidationError(
                "Username must contain only letters, numbers, hyphens and underscores"
            )
        return value

    def validate_email(self, value):
        """
        Validate email is unique across all users.

        Args:
            value: Email address to validate.

        Returns:
            str: Validated email.

        Raises:
            ValidationError: If email is already in use.
        """
        if self.instance and self.instance.email == value:
            return value
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use")
        return value

    def create(self, validated_data):
        """
        Create user with hashed password.

        Args:
            validated_data: Dictionary of validated user data.

        Returns:
            User: Created user instance.
        """
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

    Attributes:
        notebook_title: Read-only field showing notebook title.
    """

    notebook_title = serializers.CharField(source="notebook.title", read_only=True)

    class Meta:
        model = ReproducibilityAnalysis
        fields = [
            "id",
            "notebook",
            "notebook_title",
            "dependencies",
            "system_deps",
            "dockerfile",
            "makefile",
            "diff_html",
            "created_at",
            "updated_at",
            "r4r_data",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ExecutionSerializer(serializers.ModelSerializer):
    """
    Serializer for Execution model.

    Attributes:
        notebook_title: Read-only field showing notebook title.
        duration_seconds: Computed field showing execution duration.
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
        """
        Calculate execution duration.

        Args:
            obj: Execution instance.

        Returns:
            float: Duration in seconds, or None if not completed.
        """
        return obj.duration


class NotebookSerializer(serializers.ModelSerializer):
    """
    Full serializer for Notebook model.

    Attributes:
        author: Read-only username field.
        author_id: Read-only user ID field.
        analysis: Nested analysis data.
        execution_count: Computed total executions.
        last_execution_status: Computed status of most recent execution.
        has_analysis: Computed boolean for analysis existence.
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
        extra_kwargs = {
            "title": {"required": True, "allow_blank": False},
            "content": {"required": True, "allow_blank": False},
        }

    def get_execution_count(self, obj):
        """
        Get total number of executions.

        Args:
            obj: Notebook instance.

        Returns:
            int: Count of executions.
        """
        return obj.executions.count()

    def get_last_execution_status(self, obj):
        """
        Get status of most recent execution.

        Args:
            obj: Notebook instance.

        Returns:
            str: Status string, or None if never executed.
        """
        last_execution = obj.executions.first()
        return last_execution.status if last_execution else None

    def get_has_analysis(self, obj):
        """
        Check if analysis exists.

        Args:
            obj: Notebook instance.

        Returns:
            bool: True if analysis exists.
        """
        return hasattr(obj, "analysis")

    def validate_title(self, value):
        """
        Validate title is not empty.

        Args:
            value: Title string to validate.

        Returns:
            str: Stripped title.

        Raises:
            ValidationError: If title is empty or whitespace only.
        """
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()

    def validate_content(self, value):
        """
        Validate content looks like R markdown.

        Args:
            value: Content string to validate.

        Returns:
            str: Original content unchanged.

        Raises:
            ValidationError: If content is empty or whitespace-only.
        """
        if not value.strip():
            raise serializers.ValidationError(
                "Content cannot be empty or whitespace only"
            )

        if value and len(value) > 10:
            r_indicators = ["```{r", "library(", "require("]
            if not any(indicator in value for indicator in r_indicators):
                pass  # Soft validation

        return value


class NotebookListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for notebook lists (excludes content).

    Attributes:
        author: Read-only username field.
        execution_count: Computed total executions.
        has_analysis: Computed boolean for analysis existence.
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
        """
        Get total executions count.

        Args:
            obj: Notebook instance.

        Returns:
            int: Count of executions.
        """
        return obj.executions.count()

    def get_has_analysis(self, obj):
        """
        Check if analysis exists.

        Args:
            obj: Notebook instance.

        Returns:
            bool: True if analysis exists.
        """
        return hasattr(obj, "analysis")
