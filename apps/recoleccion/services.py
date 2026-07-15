"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""Lógica de negocio del módulo de recolección."""

from django.db.models import Sum

from .models import Recoleccion


def obtener_total_kg():
    """Retorna el total de kg recolectados en todo el sistema."""
    result = Recoleccion.objects.aggregate(total=Sum("kilos"))
    return result["total"] or 0


def obtener_kg_por_usuario(usuario):
    """Retorna el total de kg recolectados por un usuario específico."""
    result = Recoleccion.objects.filter(responsable=usuario).aggregate(
        total=Sum("kilos")
    )
    return result["total"] or 0
