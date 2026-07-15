"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""URLs del módulo de reportes (solo lectura)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ReporteViewSet

router = DefaultRouter()
router.register("", ReporteViewSet, basename="reportes")

urlpatterns = [
    path("", include(router.urls)),
]
