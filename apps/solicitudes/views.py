"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""
G.E.A. Backend — Views del módulo de solicitudes.

Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsAdministrativo

from .models import Solicitud
from .serializers import (
    RevisarSolicitudSerializer,
    SolicitudCreateSerializer,
    SolicitudDetailSerializer,
    SolicitudListSerializer,
)
from .services import aceptar_solicitud, rechazar_solicitud


class SolicitudViewSet(viewsets.ModelViewSet):
    """
    CRUD /api/v1/solicitudes/

    - Estudiantes crean solicitudes y ven solo las suyas.
    - Administrativos/Root ven todas y pueden aceptar/rechazar.
    """

    queryset = Solicitud.objects.select_related(
        "solicitante",
        "especie_existente",
        "arbol_existente",
        "id_area",
        "revisado_por",
    ).all()
    filterset_fields = ["status", "solicitante"]
    search_fields = ["nueva_etiqueta", "arbol_existente__etiqueta", "observaciones"]
    ordering_fields = ["fecha_solicitud", "status"]

    def get_serializer_class(self):
        if self.action == "create":
            return SolicitudCreateSerializer
        if self.action == "list":
            return SolicitudListSerializer
        if self.action == "revisar":
            return RevisarSolicitudSerializer
        return SolicitudDetailSerializer

    def get_permissions(self):
        if self.action == "revisar":
            return [IsAuthenticated(), IsAdministrativo()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        # Estudiantes solo ven sus propias solicitudes
        if user.rol == "user":
            qs = qs.filter(solicitante=user)
        return qs

    @action(detail=True, methods=["post"], url_path="revisar")
    def revisar(self, request, pk=None):
        """
        POST /api/v1/solicitudes/{id}/revisar/

        Body: { "accion": "Aceptada"|"Rechazada", "motivo_rechazo": "..." }

        Solo Administrativos y Root.
        """
        solicitud = self.get_object()

        if solicitud.status != Solicitud.Status.PENDIENTE:
            return Response(
                {"error": True, "message": "Esta solicitud ya fue revisada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RevisarSolicitudSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        accion = serializer.validated_data["accion"]

        if accion == "Aceptada":
            aceptar_solicitud(solicitud, request.user)
        else:
            motivo = serializer.validated_data.get("motivo_rechazo", "")
            rechazar_solicitud(solicitud, request.user, motivo)

        return Response(
            SolicitudDetailSerializer(solicitud).data,
            status=status.HTTP_200_OK,
        )
