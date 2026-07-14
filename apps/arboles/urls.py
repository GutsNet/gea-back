"""URLs del módulo de árboles."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ArbolViewSet, EspecieViewSet, UbicacionViewSet

router = DefaultRouter()
router.register("especies", EspecieViewSet, basename="especies")
router.register("ubicaciones", UbicacionViewSet, basename="ubicaciones")
router.register("", ArbolViewSet, basename="arboles")

urlpatterns = [
    path("", include(router.urls)),
]
