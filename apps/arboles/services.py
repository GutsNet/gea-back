"""Lógica de negocio del módulo de árboles."""

from django.db.models import Count, Q


def obtener_estadisticas_arboles():
    """Retorna estadísticas generales del catálogo de árboles."""
    from .models import Arbol

    return Arbol.objects.aggregate(
        total=Count("id"),
        sanos=Count("id", filter=Q(estado="Sano")),
        infestados=Count("id", filter=Q(estado="Infestado")),
        en_limpieza=Count("id", filter=Q(estado="Limpieza")),
        saneados=Count("id", filter=Q(estado="Saneado")),
    )


def recalcular_infestacion(arbol):
    """
    Recalcula el nivel de infestación de un árbol basándose
    en su reporte validado más reciente.

    El nivel se calcula promediando los 3 componentes (n1, n2, n3)
    de la escala Hawksworth.
    """
    ultimo_reporte = (
        arbol.reportes.filter(status_reporte="Validado").order_by("-hora").first()
    )
    if ultimo_reporte:
        promedio = (ultimo_reporte.n1 + ultimo_reporte.n2 + ultimo_reporte.n3) / 3
        arbol.nivel_infestacion = round(promedio, 2)
        arbol.save(update_fields=["nivel_infestacion", "updated_at"])
