from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notebook
from .serializers import NotebookSerializer


class NotebookViewSet(viewsets.ModelViewSet):
    serializer_class = NotebookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notebook.objects.filter(author=self.request.user)

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        notebook = self.get_object()
        return Response(
            {
                "status": "success",
                "message": "Notebook execution started",
                "notebook_id": notebook.id,
            }
        )
