"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""
Views del módulo de reportes.

Los reportes se crean automáticamente al aceptar una solicitud.
Este ViewSet es solo lectura.

Visibilidad:
    - Estudiantes ven solo sus propios reportes.
    - Administrativos/Root ven todos.
    - Desde el mapa, se consultan reportes por árbol (acceso público autenticado).
"""

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Reporte
from .serializers import ReporteListSerializer, ReporteSerializer


class ReporteViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    GET /api/v1/reportes/          → lista
    GET /api/v1/reportes/{id}/     → detalle
    GET /api/v1/reportes/?id_arbol={uuid}  → reportes de un árbol (para el mapa)

    Solo lectura. Los reportes se generan al aceptar solicitudes.
    """

    queryset = Reporte.objects.select_related("id_arbol", "responsable").all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ["id_arbol", "status_reporte", "responsable"]
    search_fields = ["id_arbol__etiqueta", "observaciones"]
    ordering_fields = ["hora"]

    def get_serializer_class(self):
        if self.action == "list":
            return ReporteListSerializer
        return ReporteSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Si se filtra por árbol, todos los autenticados pueden ver (para el mapa)
        if self.request.query_params.get("id_arbol"):
            return qs

        # Sin filtro de árbol: estudiantes solo ven los suyos
        if user.rol == "user":
            qs = qs.filter(responsable=user)
        return qs
