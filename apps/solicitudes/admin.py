"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""Registro de modelos de solicitudes en Django Admin."""

from django.contrib import admin

from .models import Solicitud


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "solicitante",
        "status",
        "es_especie_nueva",
        "es_arbol_nuevo",
        "n1",
        "n2",
        "n3",
        "fecha_solicitud",
    ]
    list_filter = ["status", "fecha_solicitud"]
    search_fields = ["solicitante__matricula", "nueva_etiqueta", "observaciones"]
    readonly_fields = ["id", "fecha_solicitud", "fecha_revision"]

    fieldsets = (
        ("General", {"fields": ("id", "solicitante", "status", "fecha_solicitud")}),
        (
            "Especie",
            {
                "fields": (
                    "especie_existente",
                    "nueva_especie_nombre",
                    "nueva_especie_nombre_cientifico",
                    "nueva_especie_nativa",
                ),
            },
        ),
        ("Árbol", {"fields": ("arbol_existente", "nueva_etiqueta", "id_area")}),
        ("Mediciones", {"fields": ("n1", "n2", "n3")}),
        (
            "Evidencia",
            {"fields": ("observaciones", "imagen1", "imagen2", "imagen3", "imagen4")},
        ),
        (
            "Revisión",
            {"fields": ("revisado_por", "fecha_revision", "motivo_rechazo")},
        ),
    )
