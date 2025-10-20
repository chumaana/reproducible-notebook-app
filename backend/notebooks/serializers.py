from rest_framework import serializers
from .models import Notebook, NotebookBlock


class NotebookBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotebookBlock
        fields = [
            "id",
            "block_type",
            "content",
            "order",
            "output",
            "created_at",
            "updated_at",
        ]


class NotebookSerializer(serializers.ModelSerializer):
    blocks = NotebookBlockSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Notebook
        fields = [
            "id",
            "title",
            "author",
            "blocks",
            "created_at",
            "updated_at",
            "is_public",
        ]

    def create(self, validated_data):
        # For now, assign to first user if no authentication
        if (
            not hasattr(self.context["request"], "user")
            or not self.context["request"].user.is_authenticated
        ):
            from django.contrib.auth.models import User

            validated_data["author"] = User.objects.first()
        else:
            validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
