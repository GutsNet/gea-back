"""Registro de modelos de recolección en Django Admin."""

from django.contrib import admin

from .models import Recoleccion


@admin.register(Recoleccion)
class RecoleccionAdmin(admin.ModelAdmin):
    list_display = ["fecha", "kilos", "responsable"]
    list_filter = ["fecha"]
    search_fields = ["responsable__matricula"]
    date_hierarchy = "fecha"
