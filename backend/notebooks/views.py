from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone


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
        print(f"DEBUG: Content length: {len(notebook.content or '')}")

        execution = Execution.objects.create(notebook=notebook, status="running")

        try:
            executor = RExecutor()
            print("DEBUG: About to call r4r executor")
            result = executor.execute_rmd(notebook.content, str(notebook.id))
            print(f"DEBUG: Result keys: {result.keys()}")

            if result["success"]:
                print(f"DEBUG: HTML length: {len(result['html'])}")
                print(f"DEBUG: HTML starts with: {result['html'][:100]}")
                print(f"DEBUG: HTML ends with: {result['html'][-100:]}")
                execution.html_output = result["html"]
                execution.status = "completed"
                execution.completed_at = timezone.now()
                execution.save()

                ReproducibilityAnalysis.objects.update_or_create(
                    notebook=notebook,
                    defaults={
                        "r4r_score": 100,
                        "dependencies": result.get("dependencies", []),
                        "system_deps": result.get("system_deps", []),
                        "dockerfile": result.get("dockerfile", ""),
                        "makefile": result.get("makefile", ""),
                    },
                )

                return Response(
                    {
                        "execution_id": execution.id,
                        "html": result["html"],
                        "dependencies": result.get("dependencies", []),
                        "dockerfile": result.get("dockerfile", ""),
                    }
                )
            else:
                execution.status = "failed"
                execution.error_message = result["error"]
                execution.completed_at = timezone.now()
                execution.save()
                return Response({"error": result["error"]}, status=400)

        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = timezone.now()
            execution.save()
            return Response({"error": str(e)}, status=500)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """Download notebook as .Rmd file"""
        notebook = self.get_object()

        response = HttpResponse(notebook.content, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="{notebook.title}.Rmd"'
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
