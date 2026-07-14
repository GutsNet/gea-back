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
    list_display = ["id", "coordenadas"]
    search_fields = ["coordenadas"]


@admin.register(Arbol)
class ArbolAdmin(admin.ModelAdmin):
    list_display = ["etiqueta", "especie", "id_area", "nivel_infestacion", "estado", "fecha_reporte"]
    list_filter = ["estado", "especie"]
    search_fields = ["etiqueta"]
    readonly_fields = ["created_at", "updated_at"]
