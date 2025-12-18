from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.http import HttpResponse, FileResponse
from django.utils import timezone
import os
import traceback  # Ensure this is imported at top level

from .models import Notebook, Execution, ReproducibilityAnalysis
from .serializers import (
    NotebookSerializer,
    UserSerializer,
    ExecutionSerializer,
    ReproducibilityAnalysisSerializer,
)
from .r_executor import RExecutor


class UserViewSet(viewsets.ModelViewSet):
    """User management endpoints"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user profile"""
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return Response({"error": "Not authenticated"}, status=401)

    @action(detail=False, methods=["post"])
    def register(self, request):
        """Register new user"""
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken"}, status=400)

        user = User.objects.create_user(
            username=username, email=email or "", password=password
        )

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=["get"])
    def notebooks(self, request, pk=None):
        """Get all notebooks by a user"""
        user = self.get_object()
        notebooks = Notebook.objects.filter(author=user)
        serializer = NotebookSerializer(notebooks, many=True)
        return Response(serializer.data)


class NotebookViewSet(viewsets.ModelViewSet):
    """Notebook CRUD + execution + analysis"""

    queryset = Notebook.objects.all().order_by("-updated_at")
    serializer_class = NotebookSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        """Execute with r4r"""
        notebook = self.get_object()

        print(f"DEBUG: Executing notebook {notebook.id}")

        execution = Execution.objects.create(notebook=notebook, status="running")

        try:
            executor = RExecutor()
            result = executor.execute_rmd(notebook.content, str(notebook.id))

            # --- SUCCESS CASE ---
            if result.get("success"):
                execution.html_output = result.get("html", "")
                execution.status = "completed"
                execution.completed_at = timezone.now()
                execution.save()

                # Save analysis
                ReproducibilityAnalysis.objects.update_or_create(
                    notebook=notebook,
                    defaults={
                        "r4r_score": 100,
                        "dependencies": result.get("detected_packages", []),
                        "system_deps": result.get("manifest", {}).get(
                            "system_packages", []
                        ),
                        "dockerfile": result.get("dockerfile", ""),
                        "makefile": result.get("makefile", ""),
                    },
                )

                # Return full result
                return Response(result)

            # --- FAILURE CASE (Fixed) ---
            else:
                execution.status = "failed"
                execution.error_message = result.get("error", "Unknown error")
                execution.completed_at = timezone.now()
                execution.save()

                # 🔥 FIX: Ми повертаємо весь result, бо він містить static_analysis!
                # Раніше ви вручну фільтрували відповідь і губили поле static_analysis.
                return Response(result, status=500)  # Використовуємо 500 або 400

        except Exception as e:
            traceback.print_exc()

            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = timezone.now()
            execution.save()

            return Response(
                {
                    "success": False,
                    "error": f"Server Error: {str(e)}",
                    "static_analysis": {},  # Empty analysis on fatal crash
                },
                status=500,
            )

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """Download notebook as .Rmd file"""
        notebook = self.get_object()

        response = HttpResponse(notebook.content, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="{notebook.title}.Rmd"'
        return response

    @action(detail=True, methods=["get"])
    def download_package(self, request, pk=None):
        """Download reproducibility package as ZIP"""
        notebook = self.get_object()
        executor = RExecutor()
        zip_path = executor.create_reproducibility_zip(str(notebook.id))

        if not zip_path or not os.path.exists(zip_path):
            return Response({"error": "Package not found"}, status=404)

        response = FileResponse(open(zip_path, "rb"), content_type="application/zip")
        response["Content-Disposition"] = (
            f'attachment; filename="notebook-{notebook.id}-reproducibility.zip"'
        )
        return response

    @action(detail=True, methods=["get"])
    def executions(self, request, pk=None):
        """Get execution history for notebook"""
        notebook = self.get_object()
        executions = Execution.objects.filter(notebook=notebook).order_by("-started_at")
        serializer = ExecutionSerializer(executions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def reproducibility(self, request, pk=None):
        """Get reproducibility analysis for notebook"""
        notebook = self.get_object()

        try:
            analysis = ReproducibilityAnalysis.objects.get(notebook=notebook)
            serializer = ReproducibilityAnalysisSerializer(analysis)
            return Response(serializer.data)
        except ReproducibilityAnalysis.DoesNotExist:
            return Response(
                {"error": "No analysis available. Run analysis first."}, status=404
            )

    @action(detail=True, methods=["get"])
    def analysis(self, request, pk=None):
        """Get reproducibility analysis files"""
        notebook = self.get_object()
        repro_dir = f"storage/notebooks/{pk}/reproducibility"

        executor = RExecutor()

        data = {
            "detected_packages": executor.detect_packages_from_content(
                notebook.content or ""
            ),
        }

        if os.path.exists(repro_dir):
            dockerfile = executor.read_file(repro_dir, "Dockerfile")
            makefile = executor.read_file(repro_dir, "Makefile")
            manifest = executor.read_json(repro_dir, "manifest.json")

            data.update(
                {
                    "dockerfile": dockerfile,
                    "dockerfile_preview": (
                        dockerfile[:300] + "..."
                        if len(dockerfile) > 300
                        else dockerfile
                    ),
                    "makefile": makefile,
                    "makefile_preview": (
                        makefile[:200] + "..." if len(makefile) > 200 else makefile
                    ),
                    "manifest": manifest,
                }
            )

        return Response(data)


class ExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """View execution history"""

    queryset = Execution.objects.all().order_by("-started_at")
    serializer_class = ExecutionSerializer
    permission_classes = [AllowAny]


class ReproducibilityAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """View reproducibility analyses"""

    queryset = ReproducibilityAnalysis.objects.all()
    serializer_class = ReproducibilityAnalysisSerializer
    permission_classes = [AllowAny]
