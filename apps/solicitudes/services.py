"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""
Lógica de negocio del módulo de solicitudes.

Contiene la lógica transaccional para aceptar/rechazar solicitudes.
Al aceptar, se crean automáticamente las entidades necesarias.
"""

from django.db import transaction
from django.utils import timezone

from apps.arboles.models import Arbol, Especie
from apps.reportes.models import Reporte


@transaction.atomic
def aceptar_solicitud(solicitud, admin):
    """
    Acepta una solicitud y crea las entidades correspondientes.

    Ejecuta en una transacción atómica:
        1. Crea Especie si es nueva
        2. Crea Árbol si es nuevo (con las imágenes de la solicitud)
        3. Crea Reporte validado
        4. Actualiza nivel_infestacion y fecha_reporte del árbol

    Args:
        solicitud: instancia de Solicitud con status Pendiente
        admin: instancia de Usuario (Administrativo/Root) que aprueba
    """
    # 1. Resolver especie
    if solicitud.es_especie_nueva:
        especie = Especie.objects.create(
            nombre=solicitud.nueva_especie_nombre,
            nombre_cientifico=solicitud.nueva_especie_nombre_cientifico,
            nativa=solicitud.nueva_especie_nativa or False,
        )
    else:
        especie = solicitud.especie_existente

    # 2. Resolver árbol
    if solicitud.es_arbol_nuevo:
        arbol = Arbol.objects.create(
            especie=especie,
            id_area=solicitud.id_area,
            etiqueta=solicitud.nueva_etiqueta,
            nivel_infestacion=solicitud.nivel_infestacion_promedio,
            estado=_calcular_estado(solicitud.nivel_infestacion_promedio),
            fecha_reporte=timezone.now().date(),
            imagen1=solicitud.imagen1,
            imagen2=solicitud.imagen2,
            imagen3=solicitud.imagen3,
            imagen4=solicitud.imagen4,
        )
    else:
        arbol = solicitud.arbol_existente

    # 3. Crear reporte validado
    Reporte.objects.create(
        id_arbol=arbol,
        responsable=solicitud.solicitante,
        n1=solicitud.n1,
        n2=solicitud.n2,
        n3=solicitud.n3,
        status_reporte=Reporte.StatusReporte.VALIDADO,
        hora=solicitud.fecha_solicitud,
        observaciones=solicitud.observaciones,
    )

    # 4. Actualizar árbol con el nuevo nivel de infestación
    nivel_infestacion = solicitud.nivel_infestacion_promedio
    arbol.nivel_infestacion = nivel_infestacion
    arbol.estado = _calcular_estado(nivel_infestacion)
    arbol.fecha_reporte = timezone.now().date()
    arbol.save(update_fields=["nivel_infestacion", "estado", "fecha_reporte", "updated_at"])

    # 5. Marcar solicitud como aceptada
    solicitud.status = solicitud.Status.ACEPTADA
    solicitud.revisado_por = admin
    solicitud.fecha_revision = timezone.now()
    solicitud.save(update_fields=["status", "revisado_por", "fecha_revision"])

    return solicitud


def rechazar_solicitud(solicitud, admin, motivo=""):
    """
    Rechaza una solicitud. No se crean entidades.

    Args:
        solicitud: instancia de Solicitud con status Pendiente
        admin: instancia de Usuario (Administrativo/Root) que rechaza
        motivo: texto explicando el motivo del rechazo
    """
    solicitud.status = solicitud.Status.RECHAZADA
    solicitud.revisado_por = admin
    solicitud.fecha_revision = timezone.now()
    solicitud.motivo_rechazo = motivo
    solicitud.save(update_fields=["status", "revisado_por", "fecha_revision", "motivo_rechazo"])

    return solicitud


def _calcular_estado(nivel_infestacion):
    """
    Determina el estado fitosanitario basándose en el nivel de infestación.

    Lógica:
        0 → Sano
        > 0 → Infestado
    """
    if nivel_infestacion == 0:
        return Arbol.Estado.SANO
    return Arbol.Estado.INFESTADO
