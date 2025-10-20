from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from .models import Notebook, NotebookBlock
from .serializers import NotebookSerializer, NotebookBlockSerializer


class NotebookViewSet(viewsets.ModelViewSet):
    queryset = Notebook.objects.all()
    serializer_class = NotebookSerializer

    @action(detail=True, methods=["post"])
    def add_block(self, request, pk=None):
        notebook = self.get_object()
        block_type = request.data.get("block_type", "code")

        # Get the highest order number and add 1
        max_order = (
            NotebookBlock.objects.filter(notebook=notebook).aggregate(
                models.Max("order")
            )["order__max"]
            or 0
        )

        block = NotebookBlock.objects.create(
            notebook=notebook, block_type=block_type, content="", order=max_order + 1
        )

        serializer = NotebookBlockSerializer(block)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def execute_block(self, request, pk=None):
        notebook = self.get_object()
        block_id = request.data.get("block_id")

        try:
            block = NotebookBlock.objects.get(id=block_id, notebook=notebook)

            if block.block_type == "code":
                # Mock R execution for now
                block.output = f'# Mock execution output\n# Code: {block.content[:50]}...\n[1] "Execution completed successfully"'
                block.save()

                serializer = NotebookBlockSerializer(block)
                return Response(serializer.data)
            else:
                return Response(
                    {"error": "Cannot execute markdown block"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except NotebookBlock.DoesNotExist:
            return Response(
                {"error": "Block not found"}, status=status.HTTP_404_NOT_FOUND
            )


class NotebookBlockViewSet(viewsets.ModelViewSet):
    queryset = NotebookBlock.objects.all()
    serializer_class = NotebookBlockSerializer
