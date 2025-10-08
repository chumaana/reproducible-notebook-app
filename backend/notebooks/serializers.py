from rest_framework import serializers
from .models import Notebook


class NotebookSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Notebook
        fields = ["id", "title", "content", "author", "created_at", "updated_at"]
        read_only_fields = ["author", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
