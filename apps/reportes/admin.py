"""Registro de modelos de reportes en Django Admin."""

from django.contrib import admin

from .models import Reporte


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ["id", "id_arbol", "n1", "n2", "n3", "status_reporte", "responsable", "hora"]
    list_filter = ["status_reporte"]
    search_fields = ["id_arbol__etiqueta", "observaciones"]
    readonly_fields = ["id"]
