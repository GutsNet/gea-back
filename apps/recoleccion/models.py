"""
Modelos del módulo de recolección de biomasa.

Registra los kg de heno motita recolectados por los estudiantes.
"""

import uuid

from django.conf import settings
from django.db import models


class Recoleccion(models.Model):
    """Registro de recolección de biomasa."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="recolecciones",
        verbose_name="Responsable",
        help_text="Estudiante que realizó la recolección.",
    )
    kilos = models.FloatField(
        "Kilos",
        help_text="Masa exacta en kg registrada en la báscula institucional.",
    )
    fecha = models.DateField(
        "Fecha",
        help_text="Fecha del registro físico y validación del pesaje.",
    )

    class Meta:
        db_table = "recolecciones"
        verbose_name = "Recolección"
        verbose_name_plural = "Recolecciones"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.fecha} — {self.kilos} kg"
