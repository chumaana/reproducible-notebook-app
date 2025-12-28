# backend/notebook_api/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from notebooks.views import (
    NotebookViewSet,
    UserLoginView,
    UserProfileView,
    UserViewSet,
    ExecutionViewSet,
    ReproducibilityAnalysisViewSet,
    UserRegisterView,
)

router = DefaultRouter()
router.register(r"notebooks", NotebookViewSet, basename="notebook")
router.register(r"users", UserViewSet, basename="user")
router.register(r"executions", ExecutionViewSet, basename="execution")
router.register(r"analyses", ReproducibilityAnalysisViewSet, basename="analysis")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", UserLoginView.as_view(), name="api-token-auth"),
    path("api/auth/register/", UserRegisterView.as_view(), name="user-register"),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("api/auth/profile/", UserProfileView.as_view(), name="user-profile"),
]
