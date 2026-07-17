"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""Registro de modelos de árboles en Django Admin."""

from django.contrib import admin

from .models import Arbol, Especie, Ubicacion


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display = ["nombre", "nombre_cientifico", "nativa"]
    list_filter = ["nativa"]
    search_fields = ["nombre", "nombre_cientifico"]


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ["id", "nombre", "coordenadas"]
    search_fields = ["nombre", "coordenadas"]


@admin.register(Arbol)
class ArbolAdmin(admin.ModelAdmin):
    list_display = ["etiqueta", "especie", "id_area", "coordenadas", "nivel_infestacion", "estado", "fecha_reporte"]
    list_filter = ["estado", "especie"]
    search_fields = ["etiqueta", "coordenadas"]
    readonly_fields = ["created_at", "updated_at"]
