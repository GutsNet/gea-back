"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""Views del módulo de árboles."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsAdministrativo

from .models import Arbol, Especie, Ubicacion
from .serializers import (
    ArbolListSerializer,
    ArbolSerializer,
    EspecieSerializer,
    UbicacionSerializer,
)


class EspecieViewSet(viewsets.ModelViewSet):
    """
    CRUD /api/v1/arboles/especies/

    Lectura: todos los autenticados.
    Escritura: administrativos y Root.
    """

    queryset = Especie.objects.all()
    serializer_class = EspecieSerializer
    search_fields = ["nombre", "nombre_cientifico"]
    filterset_fields = ["nativa"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdministrativo()]
        return [IsAuthenticated()]


class UbicacionViewSet(viewsets.ModelViewSet):
    """
    CRUD /api/v1/arboles/ubicaciones/

    Lectura: todos los autenticados.
    Escritura: administrativos y Root.
    """

    queryset = Ubicacion.objects.all()
    serializer_class = UbicacionSerializer
    search_fields = ["nombre", "coordenadas"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdministrativo()]
        return [IsAuthenticated()]


class ArbolViewSet(viewsets.ModelViewSet):
    """
    CRUD /api/v1/arboles/

    Lectura: todos los autenticados.
    Escritura: administrativos y Root.
    """

    queryset = Arbol.objects.select_related("especie", "id_area").all()
    search_fields = ["etiqueta", "especie__nombre"]
    filterset_fields = ["especie", "estado", "id_area"]
    ordering_fields = ["fecha_reporte", "nivel_infestacion", "etiqueta"]

    def get_serializer_class(self):
        if self.action == "list":
            return ArbolListSerializer
        return ArbolSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdministrativo()]
        return [IsAuthenticated()]
