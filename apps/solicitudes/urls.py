"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""URLs del módulo de solicitudes."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SolicitudViewSet

router = DefaultRouter()
router.register("", SolicitudViewSet, basename="solicitudes")

urlpatterns = [
    path("", include(router.urls)),
]
