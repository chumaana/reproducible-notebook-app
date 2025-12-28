from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.http import HttpResponse, FileResponse
from django.utils import timezone
import os
import traceback
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate

from .models import Notebook, Execution, ReproducibilityAnalysis
from .serializers import (
    NotebookSerializer,
    UserSerializer,
    ExecutionSerializer,
    ReproducibilityAnalysisSerializer,
)

# Ensure you have all 3 executors imported
from .executors import RmdExecutor, R4RExecutor, RDiffExecutor


class UserRegisterView(APIView):
    """
    POST /api/auth/register/
    Register a new user and return auth token
    """

    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not email or not password:
            return Response(
                {"error": "Please provide username, email and password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username, email=email, password=password
        )

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    User management: Registration and Profile.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "register":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def register(self, request):
        """Register new user"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotebookViewSet(viewsets.ModelViewSet):
    """
    Notebook CRUD + execution + analysis.
    Filtered by the authenticated user.
    """

    serializer_class = NotebookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Only show notebooks owned by the current user"""
        return Notebook.objects.filter(author=self.request.user).order_by("-updated_at")

    def perform_create(self, serializer):
        """Auto-assign the author on create"""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        """Step 1: Execute R code (RmdExecutor)"""
        notebook = self.get_object()
        print(f"DEBUG: Executing notebook {notebook.id}")

        execution = Execution.objects.create(notebook=notebook, status="running")

        try:
            executor = RmdExecutor()
            result = executor.execute(notebook.content, notebook.id)

            if result.get("success"):
                execution.html_output = result.get("html", "")
                execution.status = "completed"
                execution.completed_at = timezone.now()
                execution.save()

                # Save Static Analysis Issues to 'dependencies' field
                ReproducibilityAnalysis.objects.update_or_create(
                    notebook=notebook,
                    defaults={
                        "dependencies": result.get("static_analysis", {}).get(
                            "issues", []
                        ),
                    },
                )
                return Response(result)
            else:
                execution.status = "failed"
                execution.error_message = result.get("error", "Unknown error")
                execution.completed_at = timezone.now()
                execution.save()
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            traceback.print_exc()
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = timezone.now()
            execution.save()
            return Response(
                {"success": False, "error": f"Server Error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def generate_package(self, request, pk=None):
        """Step 2: Generate Docker package (R4RExecutor)"""
        notebook = self.get_object()

        try:
            executor = R4RExecutor()
            result = executor.execute(notebook.id)

            if result.get("success"):
                ReproducibilityAnalysis.objects.update_or_create(
                    notebook=notebook,
                    defaults={
                        "dockerfile": result.get("dockerfile", ""),
                        "makefile": result.get("makefile", ""),
                        "system_deps": result.get("manifest", {}).get(
                            "system_packages", []
                        ),
                    },
                )

            return Response(result)

        except Exception as e:
            traceback.print_exc()
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def generate_diff(self, request, pk=None):
        """Step 3: Generate Semantic Diff (RDiffExecutor)"""
        notebook = self.get_object()

        try:
            executor = RDiffExecutor()
            result = executor.execute(notebook.id)

            if result.get("success"):
                # Save the Diff HTML so it persists on reload
                ReproducibilityAnalysis.objects.update_or_create(
                    notebook=notebook,
                    defaults={
                        "diff_html": result.get("diff_html") or result.get("html", "")
                    },
                )

            return Response(result)

        except Exception as e:
            traceback.print_exc()
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """Download raw .Rmd file"""
        notebook = self.get_object()
        response = HttpResponse(notebook.content, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="{notebook.title}.Rmd"'
        return response

    @action(detail=True, methods=["get"])
    def download_package(self, request, pk=None):
        """Download reproducibility ZIP"""
        notebook = self.get_object()

        try:
            zip_path = f"storage/notebooks/{notebook.id}/reproducibility_package.zip"
            if not os.path.exists(zip_path):
                return Response(
                    {
                        "error": "Package not generated yet. Run 'Generate Package' first."
                    },
                    status=404,
                )

            return FileResponse(
                open(zip_path, "rb"),
                as_attachment=True,
                filename=f"notebook_{notebook.id}_package.zip",
            )
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=True, methods=["get"])
    def executions(self, request, pk=None):
        """Get history"""
        notebook = self.get_object()
        executions = Execution.objects.filter(notebook=notebook).order_by("-started_at")
        serializer = ExecutionSerializer(executions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def reproducibility(self, request, pk=None):
        """Get analysis data"""
        notebook = self.get_object()
        try:
            serializer = ReproducibilityAnalysisSerializer(notebook.analysis)
            return Response(serializer.data)
        except ReproducibilityAnalysis.DoesNotExist:
            return Response(
                {"error": "No analysis available. Run analysis first."}, status=404
            )
        except Exception:
            return Response({"status": "no_analysis"}, status=200)


class ExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ExecutionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Execution.objects.filter(notebook__author=self.request.user).order_by(
            "-started_at"
        )


class ReproducibilityAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReproducibilityAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReproducibilityAnalysis.objects.filter(
            notebook__author=self.request.user
        )


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Please provide username and password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                }
            )
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "date_joined": user.date_joined,
            }
        )

    def patch(self, request):
        user = request.user
        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        user.email = request.data.get("email", user.email)
        user.save()
        return Response(
            {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "date_joined": user.date_joined,
            }
        )
