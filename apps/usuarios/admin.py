"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""Registro de modelos de usuarios en Django Admin."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin personalizado para el modelo Usuario."""

    list_display = ["matricula", "rol", "grupo", "cuatrimestre", "estatus", "ultimo_acceso"]
    list_filter = ["rol", "estatus", "cuatrimestre"]
    search_fields = ["matricula", "username"]
    ordering = ["-fecha_registro"]

    fieldsets = UserAdmin.fieldsets + (
        (
            "G.E.A.",
            {
                "fields": ("matricula", "rol", "grupo", "cuatrimestre", "estatus", "ultimo_acceso"),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "G.E.A.",
            {
                "fields": ("matricula", "rol", "grupo", "cuatrimestre"),
            },
        ),
    )
