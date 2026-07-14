"""Views del módulo de reportes."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsAdministrativo, IsOwnerOrAdministrativo

from .models import Reporte
from .serializers import (
    ReporteListSerializer,
    ReporteSerializer,
    ValidarReporteSerializer,
)
from .services import rechazar_reporte, validar_reporte


class ReporteViewSet(viewsets.ModelViewSet):
    """
    CRUD /api/v1/reportes/

    - Estudiantes pueden crear reportes.
    - Administrativos pueden validar/rechazar.
    - Cada estudiante ve sus propios reportes; administrativos ven todos.
    """

    queryset = (
        Reporte.objects.select_related("id_arbol", "responsable").all()
    )
    filterset_fields = ["id_arbol", "status_reporte", "responsable"]
    search_fields = ["id_arbol__etiqueta", "observaciones"]
    ordering_fields = ["hora", "n1", "n2", "n3"]

    def get_serializer_class(self):
        if self.action == "list":
            return ReporteListSerializer
        if self.action == "validar":
            return ValidarReporteSerializer
        return ReporteSerializer

    def get_permissions(self):
        if self.action == "validar":
            return [IsAuthenticated(), IsAdministrativo()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsOwnerOrAdministrativo()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        # Estudiantes solo ven sus propios reportes
        if user.rol == "Estudiante":
            qs = qs.filter(responsable=user)
        return qs

    @action(detail=True, methods=["post"], url_path="validar")
    def validar(self, request, pk=None):
        """
        POST /api/v1/reportes/{id}/validar/

        Body: { "accion": "Validado"|"Rechazado" }
        """
        reporte = self.get_object()
        serializer = ValidarReporteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        accion = serializer.validated_data["accion"]

        if accion == "Validado":
            validar_reporte(reporte)
        else:
            rechazar_reporte(reporte)

        return Response(ReporteSerializer(reporte).data, status=status.HTTP_200_OK)
