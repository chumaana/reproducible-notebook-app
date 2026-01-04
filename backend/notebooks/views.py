"""
Django REST Framework views for notebook and user management.
Optimized for database performance to prevent N+1 query issues.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import (
    action,
    permission_classes as method_permission_classes,
)
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.http import HttpResponse, FileResponse
from django.utils import timezone
from django.db.models import Q
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
    """User registration endpoint."""

    permission_classes = [AllowAny]

    def post(self, request):
        # Pass data to the serializer to handle validation
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
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

        # If password is weak or username exists, this returns the specific error
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """User login endpoint."""

    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        # DEBUG LOGGING
        print(f"\n=== LOGIN ATTEMPT ===")
        print(f"Username: '{username}'")
        print(f"Password: '{password}'")
        print(f"Request data: {request.data}")

        # Check if user exists
        try:
            db_user = User.objects.get(username=username)
            print(f"User found in DB: {db_user.username}")
            print(f"User is_active: {db_user.is_active}")
            print(f"Password check: {db_user.check_password(password)}")
        except User.DoesNotExist:
            print(f"User '{username}' does NOT exist in database")
        print(f"=====================\n")

        if not username or not password:
            return Response(
                {"error": "Please provide username and password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)
        print(f"authenticate() returned: {user}")

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

        print("Authentication failed - returning error")
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
        )


class UserLogoutView(APIView):
    """User logout endpoint."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response(
                {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"detail": "Logout failed."}, status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(APIView):
    """User profile management endpoint."""

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


class UserViewSet(viewsets.ModelViewSet):
    """User management ViewSet."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "register":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IsOwnerOrReadOnlyIfPublic(permissions.BasePermission):
    """
    Custom permission:
    - Owner can do anything
    - Others can only read if public
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS and obj.is_public:
            return True
        return obj.author == request.user


class NotebookViewSet(viewsets.ModelViewSet):
    """
    Notebook management ViewSet.
    OPTIMIZED: Uses select_related/prefetch_related to prevent N+1 queries.
    """

    serializer_class = NotebookSerializer
    queryset = Notebook.objects.all()

    def get_permissions(self):
        if self.action in ["retrieve", "list", "executions", "download"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnlyIfPublic()]

    def get_queryset(self):
        """
        Get notebooks owned by current user OR that are public.
        Optimized to fetch related data in single queries.
        """
        # ✅ OPTIMIZATION: Prepare base query with eager loading
        # - select_related('author'): Joins User table
        # - prefetch_related('executions', 'analysis'): Batches related data
        base_qs = Notebook.objects.select_related("author").prefetch_related(
            "executions", "analysis"
        )

        user = self.request.user

        if user.is_authenticated:
            return (
                base_qs.filter(Q(author=user) | Q(is_public=True))
                .distinct()
                .order_by("-updated_at")
            )
        else:
            return base_qs.filter(is_public=True).order_by("-updated_at")

    def retrieve(self, request, *args, **kwargs):
        notebook = self.get_object()

        if not notebook.is_public:
            if not request.user.is_authenticated:
                return Response(
                    {"error": "Authentication required"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            if notebook.author != request.user:
                return Response(
                    {"error": "This notebook is private"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        serializer = self.get_serializer(notebook)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        notebook = self.get_object()

        if notebook.author != request.user:
            return Response(
                {"error": "Only the owner can execute this notebook"},
                status=status.HTTP_403_FORBIDDEN,
            )

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
        notebook = self.get_object()

        if notebook.author != request.user:
            return Response(
                {"error": "Only the owner can generate a package"},
                status=status.HTTP_403_FORBIDDEN,
            )

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
        notebook = self.get_object()

        if notebook.author != request.user:
            return Response(
                {"error": "Only the owner can generate diff"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            executor = RDiffExecutor()
            result = executor.execute(notebook.id)

            if result.get("success"):
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
    @method_permission_classes([AllowAny])
    def download(self, request, pk=None):
        notebook = self.get_object()

        if not notebook.is_public:
            if not request.user.is_authenticated or notebook.author != request.user:
                return Response(
                    {"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN
                )

        response = HttpResponse(notebook.content, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="{notebook.title}.Rmd"'
        return response

    @action(detail=True, methods=["get"])
    def download_package(self, request, pk=None):
        notebook = self.get_object()

        if not notebook.is_public:
            if not request.user.is_authenticated or notebook.author != request.user:
                return Response(
                    {"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN
                )

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
    @method_permission_classes([AllowAny])
    def executions(self, request, pk=None):
        """
        Get execution history for notebook.
        OPTIMIZED: Uses select_related to prevent N+1 queries.
        """
        try:
            notebook = Notebook.objects.get(pk=pk)
        except Notebook.DoesNotExist:
            return Response(
                {"error": "Notebook not found"}, status=status.HTTP_404_NOT_FOUND
            )

        is_owner = request.user.is_authenticated and notebook.author == request.user
        if not notebook.is_public and not is_owner:
            if not request.user.is_authenticated:
                return Response(
                    {"error": "Authentication credentials were not provided."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            return Response(
                {"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN
            )

        # ✅ OPTIMIZATION: select_related('notebook') prevents repeated DB hits
        # when the serializer accesses 'notebook.title'.
        executions = (
            notebook.executions.all().select_related("notebook").order_by("-started_at")
        )

        serializer = ExecutionSerializer(executions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    @method_permission_classes([AllowAny])
    def reproducibility(self, request, pk=None):
        try:
            notebook = Notebook.objects.get(pk=pk)
        except Notebook.DoesNotExist:
            return Response(
                {"error": "Notebook not found"}, status=status.HTTP_404_NOT_FOUND
            )

        is_owner = request.user.is_authenticated and notebook.author == request.user
        if not notebook.is_public and not is_owner:
            if not request.user.is_authenticated:
                return Response(
                    {"error": "Authentication required"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            return Response(
                {"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            serializer = ReproducibilityAnalysisSerializer(notebook.analysis)
            return Response(serializer.data)
        except ReproducibilityAnalysis.DoesNotExist:
            return Response(
                {"error": "No analysis available. Run analysis first."}, status=404
            )
        except Exception:
            return Response({"status": "no_analysis"}, status=200)

    @action(detail=True, methods=["post"])
    def toggle_public(self, request, pk=None):
        notebook = self.get_object()
        if notebook.author != request.user:
            return Response(
                {"error": "Only the owner can change public status"},
                status=status.HTTP_403_FORBIDDEN,
            )

        notebook.is_public = not notebook.is_public
        notebook.save()
        return Response(
            {
                "is_public": notebook.is_public,
                "message": f'Notebook is now {"public" if notebook.is_public else "private"}',
            }
        )


class ExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for execution records.
    OPTIMIZED: Uses select_related to prevent N+1 queries.
    """

    serializer_class = ExecutionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get executions for current user's notebooks.
        Optimized with select_related.
        """
        # ✅ OPTIMIZATION: Fetch notebook and author details in the main query
        return (
            Execution.objects.filter(notebook__author=self.request.user)
            .select_related("notebook", "notebook__author")
            .order_by("-started_at")
        )


class ReproducibilityAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for reproducibility analyses."""

    serializer_class = ReproducibilityAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReproducibilityAnalysis.objects.filter(
            notebook__author=self.request.user
        )
