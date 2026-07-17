"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""
G.E.A. Backend — Módulo de solicitudes.

Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)

Un estudiante envía una solicitud que puede incluir una especie nueva
y/o un árbol nuevo. Un admin/root la revisa y, al aceptarla, el sistema
crea las entidades correspondientes en las tablas principales.
"""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Solicitud(models.Model):
    """
    Solicitud de reporte de infestación.

    Flujo:
        1. Estudiante envía solicitud (status=Pendiente)
        2. Admin/Root revisa
        3. Si acepta → se crean Especie/Árbol/Reporte automáticamente
        4. Si rechaza → se registra motivo, no se crean entidades
    """

    class Status(models.TextChoices):
        PENDIENTE = "Pendiente", "Pendiente"
        ACEPTADA = "Aceptada", "Aceptada"
        RECHAZADA = "Rechazada", "Rechazada"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="solicitudes",
        verbose_name="Solicitante",
    )
    status = models.CharField(
        "Estatus",
        max_length=15,
        choices=Status.choices,
        default=Status.PENDIENTE,
    )
    fecha_solicitud = models.DateTimeField(
        "Fecha de solicitud",
        auto_now_add=True,
    )

    # ── Especie (existente o nueva) ──────────────────
    especie_existente = models.ForeignKey(
        "arboles.Especie",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitudes",
        verbose_name="Especie existente",
        help_text="Seleccionar si la especie ya está registrada.",
    )
    nueva_especie_nombre = models.CharField(
        "Nueva especie — nombre común",
        max_length=100,
        blank=True,
        default="",
    )
    nueva_especie_nombre_cientifico = models.CharField(
        "Nueva especie — nombre científico",
        max_length=150,
        blank=True,
        default="",
    )
    nueva_especie_nativa = models.BooleanField(
        "Nueva especie — ¿es nativa?",
        null=True,
        blank=True,
    )

    # ── Árbol (existente o nuevo) ────────────────────
    arbol_existente = models.ForeignKey(
        "arboles.Arbol",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitudes",
        verbose_name="Árbol existente",
        help_text="Seleccionar si el árbol ya está registrado.",
    )
    nueva_etiqueta = models.CharField(
        "Nueva etiqueta del árbol",
        max_length=50,
        blank=True,
        default="",
        help_text="Código alfanumérico del árbol si es un árbol nuevo.",
    )
    id_area = models.ForeignKey(
        "arboles.Ubicacion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitudes",
        verbose_name="Ubicación del nuevo árbol",
    )
    coordenadas_exactas = models.CharField(
        "Coordenadas exactas del árbol",
        max_length=500,
        blank=True,
        default="",
        help_text="Punto exacto del árbol en formato lat,long o x,y.",
    )

    # ── Mediciones Hawksworth ────────────────────────
    n1 = models.FloatField(
        "Nivel 1 (Hawksworth)",
        validators=[MinValueValidator(0.0), MaxValueValidator(2.5)],
    )
    n2 = models.FloatField(
        "Nivel 2 (Hawksworth)",
        validators=[MinValueValidator(0.0), MaxValueValidator(2.5)],
    )
    n3 = models.FloatField(
        "Nivel 3 (Hawksworth)",
        validators=[MinValueValidator(0.0), MaxValueValidator(2.5)],
    )

    # ── Evidencia ────────────────────────────────────
    observaciones = models.TextField(
        "Observaciones",
        blank=True,
        default="",
    )
    imagen1 = models.CharField("Imagen 1", max_length=500, blank=True, default="")
    imagen2 = models.CharField("Imagen 2", max_length=500, blank=True, default="")
    imagen3 = models.CharField("Imagen 3", max_length=500, blank=True, default="")
    imagen4 = models.CharField("Imagen 4", max_length=500, blank=True, default="")

    # ── Revisión admin ───────────────────────────────
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitudes_revisadas",
        verbose_name="Revisado por",
    )
    fecha_revision = models.DateTimeField(
        "Fecha de revisión",
        null=True,
        blank=True,
    )
    motivo_rechazo = models.TextField(
        "Motivo de rechazo",
        blank=True,
        default="",
    )

    class Meta:
        db_table = "solicitudes"
        verbose_name = "Solicitud"
        verbose_name_plural = "Solicitudes"
        ordering = ["-fecha_solicitud"]

    def __str__(self):
        return f"Solicitud {str(self.pk)[:8]} — {self.solicitante.matricula} ({self.status})"

    @property
    def es_especie_nueva(self):
        """True si la solicitud propone una especie nueva."""
        return self.especie_existente is None and bool(self.nueva_especie_nombre)

    @property
    def es_arbol_nuevo(self):
        """True si la solicitud propone un árbol nuevo."""
        return self.arbol_existente is None and bool(self.nueva_etiqueta)

    @property
    def nivel_infestacion_promedio(self):
        """Calcula la suma de los 3 componentes Hawksworth (máximo 7.5)."""
        return round(self.n1 + self.n2 + self.n3, 2)
