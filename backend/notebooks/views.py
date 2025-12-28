"""
Django REST Framework views for notebook and user management.
"""

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
from .executors import RmdExecutor, R4RExecutor, RDiffExecutor


class UserRegisterView(APIView):
    """
    User registration endpoint.

    Handles new user registration and returns authentication token.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Register a new user.

        Args:
            request: HTTP request with username, email, password in body.

        Returns:
            Response with token and user data, or error message.
        """
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


class UserLoginView(APIView):
    """
    User login endpoint.

    Authenticates user and returns token.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticate user and return token.

        Args:
            request: HTTP request with username and password.

        Returns:
            Response with token and user data, or error message.
        """
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
    """
    User profile management endpoint.

    Allows viewing and updating user profile information.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Get current user profile.

        Args:
            request: HTTP request with authenticated user.

        Returns:
            Response with user profile data.
        """
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
        """
        Update user profile.

        Args:
            request: HTTP request with profile fields to update.

        Returns:
            Response with updated user profile data.
        """
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


class UserViewSet(viewsets.ModelViewSet):
    """
    User management ViewSet.

    Provides registration and profile endpoints.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Set permissions based on action.

        Returns:
            List of permission classes.
        """
        if self.action == "register":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        Get current user profile.

        Args:
            request: HTTP request.

        Returns:
            Response with serialized user data.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def register(self, request):
        """
        Register new user.

        Args:
            request: HTTP request with user data.

        Returns:
            Response with created user data or validation errors.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotebookViewSet(viewsets.ModelViewSet):
    """
    Notebook management ViewSet.

    Provides CRUD operations and reproducibility actions for notebooks.
    Automatically filters notebooks by authenticated user.
    """

    serializer_class = NotebookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get notebooks owned by current user.

        Returns:
            QuerySet of notebooks filtered by author.
        """
        return Notebook.objects.filter(author=self.request.user).order_by("-updated_at")

    def perform_create(self, serializer):
        """
        Auto-assign author when creating notebook.

        Args:
            serializer: NotebookSerializer instance.
        """
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        """
        Execute R Markdown notebook and perform static analysis.

        Args:
            request: HTTP request.
            pk: Notebook primary key.

        Returns:
            Response with execution results or error.
        """
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

                # Save static analysis results
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
        """
        Generate reproducibility package with Docker files.

        Args:
            request: HTTP request.
            pk: Notebook primary key.

        Returns:
            Response with generation results or error.
        """
        notebook = self.get_object()

        try:
            executor = R4RExecutor()
            result = executor.execute(notebook.id)

            if result.get("success"):
                # Save r4r analysis data
                ReproducibilityAnalysis.objects.update_or_create(
                    notebook=notebook,
                    defaults={
                        "dockerfile": result.get("dockerfile", ""),
                        "makefile": result.get("makefile", ""),
                        "system_deps": result.get("manifest", {}).get(
                            "system_packages", []
                        ),
                        "r4r_data": result.get("r4r_data", {}),
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
        """
        Generate semantic diff visualization.

        Args:
            request: HTTP request.
            pk: Notebook primary key.

        Returns:
            Response with diff HTML or error.
        """
        notebook = self.get_object()

        try:
            executor = RDiffExecutor()
            result = executor.execute(notebook.id)

            if result.get("success"):
                # Save diff HTML
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
        """
        Download notebook as .Rmd file.

        Args:
            request: HTTP request.
            pk: Notebook primary key.

        Returns:
            HttpResponse with .Rmd file attachment.
        """
        notebook = self.get_object()
        response = HttpResponse(notebook.content, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="{notebook.title}.Rmd"'
        return response

    @action(detail=True, methods=["get"])
    def download_package(self, request, pk=None):
        """
        Download reproducibility package as ZIP.

        Args:
            request: HTTP request.
            pk: Notebook primary key.

        Returns:
            FileResponse with ZIP attachment or error.
        """
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
        """
        Get execution history for notebook.

        Args:
            request: HTTP request.
            pk: Notebook primary key.

        Returns:
            Response with list of executions.
        """
        notebook = self.get_object()
        executions = Execution.objects.filter(notebook=notebook).order_by("-started_at")
        serializer = ExecutionSerializer(executions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def reproducibility(self, request, pk=None):
        """
        Get reproducibility analysis data.

        Args:
            request: HTTP request.
            pk: Notebook primary key.

        Returns:
            Response with analysis data or error.
        """
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
    """
    Read-only ViewSet for execution records.

    Filtered by authenticated user's notebooks.
    """

    serializer_class = ExecutionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get executions for current user's notebooks.

        Returns:
            QuerySet of executions filtered by notebook author.
        """
        return Execution.objects.filter(notebook__author=self.request.user).order_by(
            "-started_at"
        )


class ReproducibilityAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for reproducibility analyses.

    Filtered by authenticated user's notebooks.
    """

    serializer_class = ReproducibilityAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get analyses for current user's notebooks.

        Returns:
            QuerySet of analyses filtered by notebook author.
        """
        return ReproducibilityAnalysis.objects.filter(
            notebook__author=self.request.user
        )
