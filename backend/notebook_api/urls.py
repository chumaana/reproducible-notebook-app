from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from notebooks.views import (
    NotebookViewSet,
    UserViewSet,
    ExecutionViewSet,
    ReproducibilityAnalysisViewSet,
)

# Create router
router = DefaultRouter()
router.register(r"notebooks", NotebookViewSet, basename="notebook")
router.register(r"users", UserViewSet, basename="user")
router.register(r"executions", ExecutionViewSet, basename="execution")
router.register(r"analyses", ReproducibilityAnalysisViewSet, basename="analysis")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
