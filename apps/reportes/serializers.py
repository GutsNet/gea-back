"""Serializers del módulo de reportes."""

from rest_framework import serializers

from .models import Reporte


class ReporteListSerializer(serializers.ModelSerializer):
    """Serializer compacto para listado de reportes."""

    arbol_etiqueta = serializers.CharField(source="id_arbol.etiqueta", read_only=True)
    responsable_matricula = serializers.CharField(source="responsable.matricula", read_only=True)
    nivel_promedio = serializers.FloatField(source="nivel_infestacion_promedio", read_only=True)

    class Meta:
        model = Reporte
        fields = [
            "id",
            "id_arbol",
            "arbol_etiqueta",
            "n1",
            "n2",
            "n3",
            "nivel_promedio",
            "status_reporte",
            "hora",
            "responsable_matricula",
        ]


class ReporteSerializer(serializers.ModelSerializer):
    """Serializer completo de reporte (detalle)."""

    arbol_etiqueta = serializers.CharField(source="id_arbol.etiqueta", read_only=True)
    responsable_matricula = serializers.CharField(source="responsable.matricula", read_only=True)
    nivel_promedio = serializers.FloatField(source="nivel_infestacion_promedio", read_only=True)

    class Meta:
        model = Reporte
        fields = [
            "id",
            "id_arbol",
            "arbol_etiqueta",
            "responsable",
            "responsable_matricula",
            "n1",
            "n2",
            "n3",
            "nivel_promedio",
            "status_reporte",
            "hora",
            "observaciones",
        ]
        read_only_fields = ["id", "responsable"]

    def create(self, validated_data):
        validated_data["responsable"] = self.context["request"].user
        return super().create(validated_data)


class ValidarReporteSerializer(serializers.Serializer):
    """Serializer para la acción de validar/rechazar un reporte."""

    accion = serializers.ChoiceField(choices=["Validado", "Rechazado"])
