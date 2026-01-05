# backend/notebook_api/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from notebooks.views import (
    NotebookViewSet,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    UserViewSet,
    ExecutionViewSet,
    ReproducibilityAnalysisViewSet,
    UserRegisterView,
)

router = DefaultRouter()
router.register(r"notebooks", NotebookViewSet, basename="notebook")
router.register(r"users", UserViewSet, basename="user")
router.register(r"analyses", ReproducibilityAnalysisViewSet, basename="analysis")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", UserLoginView.as_view(), name="api-token-auth"),
    path("api/auth/register/", UserRegisterView.as_view(), name="user-register"),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("api/auth/profile/", UserProfileView.as_view(), name="user-profile"),
    path("api/auth/logout/", UserLogoutView.as_view(), name="logout"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
