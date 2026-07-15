"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""URLs del módulo de recolección."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RecoleccionViewSet

router = DefaultRouter()
router.register("", RecoleccionViewSet, basename="recoleccion")

urlpatterns = [
    path("", include(router.urls)),
]
