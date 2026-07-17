"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""Serializers del módulo de recolección."""

from rest_framework import serializers

from .models import Recoleccion


class RecoleccionSerializer(serializers.ModelSerializer):
    """Serializer de registro de recolección."""

    responsable_matricula = serializers.CharField(source="responsable.matricula", read_only=True)

    class Meta:
        model = Recoleccion
        fields = [
            "id",
            "responsable",
            "responsable_matricula",
            "kilos",
            "fecha",
        ]
        read_only_fields = ["id"]

    def validate_responsable(self, usuario):
        if usuario.rol != "Estudiante":
            raise serializers.ValidationError(
                "El responsable de una recolección debe ser un estudiante."
            )
        return usuario
