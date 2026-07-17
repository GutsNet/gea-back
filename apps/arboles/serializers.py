"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""Serializers del módulo de árboles."""

from rest_framework import serializers

from .models import Arbol, Especie, Ubicacion


class EspecieSerializer(serializers.ModelSerializer):
    """Serializer de especie arbórea."""

    class Meta:
        model = Especie
        fields = ["id", "nombre", "nombre_cientifico", "nativa"]


class UbicacionSerializer(serializers.ModelSerializer):
    """Serializer de ubicación (celda Voronoi)."""

    class Meta:
        model = Ubicacion
        fields = ["id", "nombre", "coordenadas"]


class ArbolListSerializer(serializers.ModelSerializer):
    """Serializer para listado de árboles (compacto)."""

    especie_nombre = serializers.CharField(source="especie.nombre", read_only=True)

    class Meta:
        model = Arbol
        fields = [
            "id",
            "etiqueta",
            "especie",
            "especie_nombre",
            "id_area",
            "coordenadas",
            "nivel_infestacion",
            "estado",
            "fecha_reporte",
        ]


class ArbolSerializer(serializers.ModelSerializer):
    """Serializer completo de árbol (detalle)."""

    especie_detail = EspecieSerializer(source="especie", read_only=True)
    ubicacion_detail = UbicacionSerializer(source="id_area", read_only=True)

    class Meta:
        model = Arbol
        fields = [
            "id",
            "etiqueta",
            "especie",
            "especie_detail",
            "id_area",
            "ubicacion_detail",
            "coordenadas",
            "nivel_infestacion",
            "estado",
            "fecha_reporte",
            "imagen1",
            "imagen2",
            "imagen3",
            "imagen4",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
