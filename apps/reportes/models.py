"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""
Modelos del módulo de reportes de infestación.

Un estudiante registra un reporte con 3 mediciones Hawksworth (n1, n2, n3)
para un árbol, y un administrativo lo valida o rechaza.
"""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Reporte(models.Model):
    """
    Reporte de infestación para un árbol específico.

    Usa la escala Hawksworth con 3 componentes (n1, n2, n3)
    que representan mediciones en distintas secciones de la copa.
    """

    class StatusReporte(models.TextChoices):
        VALIDADO = "Validado", "Validado"
        RECHAZADO = "Rechazado", "Rechazado"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    id_arbol = models.ForeignKey(
        "arboles.Arbol",
        on_delete=models.CASCADE,
        related_name="reportes",
        verbose_name="Árbol",
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reportes",
        verbose_name="Responsable",
    )
    n1 = models.FloatField(
        "Nivel 1 (Hawksworth)",
        help_text="Medición Hawksworth — componente 1. Rango válido: 0.0 a 2.5.",
        validators=[MinValueValidator(0.0), MaxValueValidator(2.5)],
    )
    n2 = models.FloatField(
        "Nivel 2 (Hawksworth)",
        help_text="Medición Hawksworth — componente 2. Rango válido: 0.0 a 2.5.",
        validators=[MinValueValidator(0.0), MaxValueValidator(2.5)],
    )
    n3 = models.FloatField(
        "Nivel 3 (Hawksworth)",
        help_text="Medición Hawksworth — componente 3. Rango válido: 0.0 a 2.5.",
        validators=[MinValueValidator(0.0), MaxValueValidator(2.5)],
    )
    status_reporte = models.CharField(
        "Estatus del reporte",
        max_length=15,
        choices=StatusReporte.choices,
    )
    hora = models.DateTimeField(
        "Hora del reporte",
        help_text="Timestamp exacto de transmisión del reporte desde el dispositivo.",
    )
    observaciones = models.TextField(
        "Observaciones",
        blank=True,
        default="",
        help_text="Notas complementarias sobre el estado físico del espécimen.",
    )

    class Meta:
        db_table = "reportes"
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        ordering = ["-hora"]

    def __str__(self):
        return f"Reporte {str(self.pk)[:8]} — {self.id_arbol.etiqueta}"

    @property
    def nivel_infestacion_promedio(self):
        """Calcula la suma de los 3 componentes Hawksworth (máximo 7.5)."""
        return round(self.n1 + self.n2 + self.n3, 2)
