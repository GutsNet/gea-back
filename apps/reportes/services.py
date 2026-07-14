"""Lógica de negocio del módulo de reportes."""

from apps.arboles.services import recalcular_infestacion

from .models import Reporte


def validar_reporte(reporte):
    """
    Valida un reporte de infestación.

    Al validar, se recalcula el nivel de infestación del árbol asociado.
    """
    reporte.status_reporte = Reporte.StatusReporte.VALIDADO
    reporte.save(update_fields=["status_reporte"])

    # Recalcular el nivel de infestación del árbol
    recalcular_infestacion(reporte.id_arbol)

    return reporte


def rechazar_reporte(reporte):
    """Rechaza un reporte de infestación."""
    reporte.status_reporte = Reporte.StatusReporte.RECHAZADO
    reporte.save(update_fields=["status_reporte"])

    return reporte
