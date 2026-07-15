"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""URLs del dashboard."""

from django.urls import path

from .views import (
    EspeciesAfectadasView,
    EvolucionReportesView,
    MapaCalorView,
    ResumenView,
)

urlpatterns = [
    path("resumen/", ResumenView.as_view(), name="dashboard-resumen"),
    path("evolucion-reportes/", EvolucionReportesView.as_view(), name="dashboard-evolucion"),
    path("mapa-calor/", MapaCalorView.as_view(), name="dashboard-mapa-calor"),
    path("especies-afectadas/", EspeciesAfectadasView.as_view(), name="dashboard-especies"),
]
