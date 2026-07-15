"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""
G.E.A. Backend — Serializers del módulo de solicitudes.

Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

from rest_framework import serializers

from .models import Solicitud


class SolicitudCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para que un estudiante cree una solicitud.

    Validaciones:
        - Debe tener especie_existente O los campos nueva_especie_*
        - Debe tener arbol_existente O (nueva_etiqueta + id_area)
        - Si tiene arbol_existente, se ignoran los campos de especie nueva
    """

    class Meta:
        model = Solicitud
        fields = [
            "id",
            # Especie
            "especie_existente",
            "nueva_especie_nombre",
            "nueva_especie_nombre_cientifico",
            "nueva_especie_nativa",
            # Árbol
            "arbol_existente",
            "nueva_etiqueta",
            "id_area",
            # Mediciones
            "n1",
            "n2",
            "n3",
            # Evidencia
            "observaciones",
            "imagen1",
            "imagen2",
            "imagen3",
            "imagen4",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        arbol_existente = data.get("arbol_existente")
        nueva_etiqueta = data.get("nueva_etiqueta", "")
        especie_existente = data.get("especie_existente")
        nueva_especie = data.get("nueva_especie_nombre", "")

        # Si el árbol ya existe, no necesitamos validar especie
        if arbol_existente:
            return data

        # Si el árbol es nuevo, necesita etiqueta + ubicación + especie
        if nueva_etiqueta:
            if not data.get("id_area"):
                raise serializers.ValidationError(
                    {"id_area": "Se requiere una ubicación para un árbol nuevo."}
                )
            if not especie_existente and not nueva_especie:
                raise serializers.ValidationError(
                    "Se requiere una especie (existente o nueva) para un árbol nuevo."
                )
        else:
            raise serializers.ValidationError(
                "Debes seleccionar un árbol existente o ingresar los datos de uno nuevo."
            )

        # Si la especie es nueva, necesita nombre científico
        if nueva_especie and not data.get("nueva_especie_nombre_cientifico"):
            raise serializers.ValidationError(
                {"nueva_especie_nombre_cientifico": "El nombre científico es requerido para una especie nueva."}
            )

        return data

    def create(self, validated_data):
        validated_data["solicitante"] = self.context["request"].user
        return super().create(validated_data)


class SolicitudListSerializer(serializers.ModelSerializer):
    """Serializer compacto para listado de solicitudes."""

    solicitante_matricula = serializers.CharField(source="solicitante.matricula", read_only=True)
    nivel_infestacion = serializers.FloatField(source="nivel_infestacion_promedio", read_only=True)
    es_especie_nueva = serializers.BooleanField(read_only=True)
    es_arbol_nuevo = serializers.BooleanField(read_only=True)

    class Meta:
        model = Solicitud
        fields = [
            "id",
            "solicitante_matricula",
            "status",
            "fecha_solicitud",
            "arbol_existente",
            "nueva_etiqueta",
            "es_especie_nueva",
            "es_arbol_nuevo",
            "n1",
            "n2",
            "n3",
            "nivel_infestacion",
        ]


class SolicitudDetailSerializer(serializers.ModelSerializer):
    """Serializer completo de solicitud (detalle)."""

    solicitante_matricula = serializers.CharField(source="solicitante.matricula", read_only=True)
    revisado_por_matricula = serializers.CharField(
        source="revisado_por.matricula", read_only=True, default=None
    )
    nivel_infestacion = serializers.FloatField(source="nivel_infestacion_promedio", read_only=True)
    es_especie_nueva = serializers.BooleanField(read_only=True)
    es_arbol_nuevo = serializers.BooleanField(read_only=True)

    class Meta:
        model = Solicitud
        fields = [
            "id",
            "solicitante",
            "solicitante_matricula",
            "status",
            "fecha_solicitud",
            # Especie
            "especie_existente",
            "nueva_especie_nombre",
            "nueva_especie_nombre_cientifico",
            "nueva_especie_nativa",
            "es_especie_nueva",
            # Árbol
            "arbol_existente",
            "nueva_etiqueta",
            "id_area",
            "es_arbol_nuevo",
            # Mediciones
            "n1",
            "n2",
            "n3",
            "nivel_infestacion",
            # Evidencia
            "observaciones",
            "imagen1",
            "imagen2",
            "imagen3",
            "imagen4",
            # Revisión
            "revisado_por",
            "revisado_por_matricula",
            "fecha_revision",
            "motivo_rechazo",
        ]
        read_only_fields = [
            "id",
            "solicitante",
            "status",
            "fecha_solicitud",
            "revisado_por",
            "fecha_revision",
            "motivo_rechazo",
        ]


class RevisarSolicitudSerializer(serializers.Serializer):
    """Serializer para la acción de aceptar/rechazar una solicitud."""

    accion = serializers.ChoiceField(choices=["Aceptada", "Rechazada"])
    motivo_rechazo = serializers.CharField(required=False, allow_blank=True, default="")
