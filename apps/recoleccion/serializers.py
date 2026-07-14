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
        read_only_fields = ["id", "responsable"]

    def create(self, validated_data):
        validated_data["responsable"] = self.context["request"].user
        return super().create(validated_data)
