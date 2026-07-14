"""Views del módulo de recolección."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsOwnerOrAdministrativo

from .models import Recoleccion
from .serializers import RecoleccionSerializer


class RecoleccionViewSet(viewsets.ModelViewSet):
    """
    CRUD /api/v1/recoleccion/

    Estudiantes registran sus recolecciones.
    Administrativos ven todas las recolecciones.
    """

    queryset = Recoleccion.objects.select_related("responsable").all()
    serializer_class = RecoleccionSerializer
    filterset_fields = ["responsable", "fecha"]
    ordering_fields = ["fecha", "kilos"]

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsOwnerOrAdministrativo()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.rol == "Estudiante":
            qs = qs.filter(responsable=user)
        return qs
