from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotebookViewSet, NotebookBlockViewSet

router = DefaultRouter()
router.register(r"notebooks", NotebookViewSet, basename="notebook")
router.register(r"blocks", NotebookBlockViewSet, basename="block")

urlpatterns = [
    path("", include(router.urls)),
]
