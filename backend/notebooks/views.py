"""
Django REST Framework views for notebook and user management.
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


class UserLogoutView(APIView):
    """
    User logout endpoint.

    Deletes user's authentication token.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Logout user by deleting their auth token.

        Args:
            request: HTTP request.

        Returns:
            Response with success message.
        """
        try:
            # Delete the user's token
            request.user.auth_token.delete()
            return Response(
                {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": "Logout failed."}, status=status.HTTP_400_BAD_REQUEST
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


class IsOwnerOrReadOnlyIfPublic(permissions.BasePermission):
    """
    Custom permission:
    - Owner can do anything
    - Others can only read if public
    """

    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions.

        Args:
            request: HTTP request.
            view: View instance.
            obj: Notebook object being accessed.

        Returns:
            bool: True if permission granted.
        """
        # Read permissions for public notebooks (anyone can read)
        if request.method in permissions.SAFE_METHODS and obj.is_public:
            return True

        # Write permissions only for owner
        return obj.author == request.user


class NotebookViewSet(viewsets.ModelViewSet):
    """
    Notebook management ViewSet.

    Provides CRUD operations and reproducibility actions for notebooks.
    Automatically filters notebooks by authenticated user or shows public ones.
    """

    serializer_class = NotebookSerializer
    queryset = Notebook.objects.all()

    def get_permissions(self):
        """
        Allow unauthenticated GET requests for public notebooks.
        Require authentication for all other operations.

        Returns:
            List of permission classes.
        """
        if self.action in ["retrieve", "list", "executions"]:  # GET requests
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnlyIfPublic()]

    def get_queryset(self):
        """
        Get notebooks owned by current user OR that are public.

        Returns:
            QuerySet of notebooks filtered by ownership or public status.
        """
        user = self.request.user

        if user.is_authenticated:
            # Authenticated users see their own + public notebooks
            return (
                Notebook.objects.filter(Q(author=user) | Q(is_public=True))
                .distinct()
                .order_by("-updated_at")
            )
        else:
            # Unauthenticated users only see public notebooks
            return Notebook.objects.filter(is_public=True).order_by("-updated_at")

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a notebook.
        Public notebooks: accessible to anyone
        Private notebooks: only accessible to owner

        Args:
            request: HTTP request.

        Returns:
            Response with notebook data or error.
        """
        notebook = self.get_object()

        # Check access permissions for private notebooks
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

        # Only owner can execute
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

        # Only owner can generate package
        if notebook.author != request.user:
            return Response(
                {"error": "Only the owner can generate a package"},
                status=status.HTTP_403_FORBIDDEN,
            )

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

        # Only owner can generate diff
        if notebook.author != request.user:
            return Response(
                {"error": "Only the owner can generate diff"},
                status=status.HTTP_403_FORBIDDEN,
            )

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
    @method_permission_classes([AllowAny])
    def download(self, request, pk=None):
        """
        Download notebook as .Rmd file.
        Public notebooks can be downloaded by anyone.

        Args:
            request: HTTP request.
            pk: Notebook primary key.

        Returns:
            HttpResponse with .Rmd file attachment.
        """
        notebook = self.get_object()

        # Check access for private notebooks
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
        """
        Download reproducibility package as ZIP.

        Args:
            request: HTTP request.
            pk: Notebook primary key.

        Returns:
            FileResponse with ZIP attachment or error.
        """
        notebook = self.get_object()

        # Check access for private notebooks
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
        Accessible if notebook is public or user is the owner.

        Args:
            request: HTTP request.
            pk: Notebook primary key.

        Returns:
            Response with list of executions.
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
        executions = Execution.objects.filter(notebook=notebook).order_by("-started_at")
        print(executions)
        serializer = ExecutionSerializer(executions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    @method_permission_classes([AllowAny])
    def reproducibility(self, request, pk=None):
        """
        Get reproducibility analysis data.
        Accessible if notebook is public or user is the owner.

        Args:
            request: HTTP request.
            pk: Notebook primary key.

        Returns:
            Response with analysis data or error.
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
        """
        Toggle public status of notebook.

        Args:
            request: HTTP request.
            pk: Notebook primary key.

        Returns:
            Response with is_public status and message.
        """
        notebook = self.get_object()

        # Only owner can toggle public status
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
