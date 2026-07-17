"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""
Modelos del módulo de árboles.

Catálogo de árboles del campus, especies, ubicaciones (celdas Voronoi)
y su estado fitosanitario.
"""

import uuid

from django.db import models

from apps.core.mixins import TimestampMixin


class Especie(models.Model):
    """Especie arbórea catalogada en el campus."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    nombre = models.CharField(
        "Nombre común",
        max_length=100,
        help_text="Nombre común u ordinario por el cual la comunidad identifica la planta.",
    )
    nombre_cientifico = models.CharField(
        "Nombre científico",
        max_length=150,
        unique=True,
        help_text="Nomenclatura binominal científica formal.",
    )
    nativa = models.BooleanField(
        "¿Es nativa?",
        default=False,
        help_text="True si la especie es originaria de la región, False si es introducida.",
    )

    class Meta:
        db_table = "especies"
        verbose_name = "Especie"
        verbose_name_plural = "Especies"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.nombre_cientifico})"


class Ubicacion(models.Model):
    """
    Área/celda geométrica de Voronoi del campus.

    Cada ubicación agrupa un conjunto de árboles en una zona delimitada.
    El campo coordenadas es un dato compuesto (VARCHAR) que contiene
    la estructura de datos geoespacial necesaria para la representación.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    nombre = models.CharField(
        "Nombre",
        max_length=100,
        unique=True,
        help_text="Nombre amigable para identificar la ubicación dentro del campus.",
    )
    coordenadas = models.CharField(
        "Coordenadas",
        max_length=500,
        unique=True,
        help_text="Estructura de datos compuesta con la información geoespacial del área.",
    )

    class Meta:
        db_table = "ubicaciones"
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"

    def __str__(self):
        return self.nombre or f"Área {str(self.id)[:8]}"


class Arbol(TimestampMixin, models.Model):
    """
    Árbol individual registrado en el campus UTTT.

    Cada árbol pertenece a una
    especie y está asociado a una celda de Voronoi (Ubicación).
    """

    class Estado(models.TextChoices):
        SANO = "Sano", "Sano"
        INFESTADO = "Infestado", "Infestado"
        LIMPIEZA = "Limpieza", "Limpieza"
        SANEADO = "Saneado", "Saneado"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    especie = models.ForeignKey(
        Especie,
        on_delete=models.PROTECT,
        related_name="arboles",
        verbose_name="Especie",
    )
    id_area = models.ForeignKey(
        Ubicacion,
        on_delete=models.PROTECT,
        related_name="arboles",
        verbose_name="Ubicación",
    )
    coordenadas = models.CharField(
        "Coordenadas exactas",
        max_length=500,
        blank=True,
        default="",
        help_text="Punto exacto del árbol en formato lat,long o x,y.",
    )
    etiqueta = models.CharField(
        "Etiqueta",
        max_length=50,
        help_text="Código alfanumérico del árbol.",
    )
    nivel_infestacion = models.FloatField(
        "Nivel de infestación",
        default=0.0,
        help_text="Suma de los tres niveles Hawksworth del último censo. Rango válido: 0.0 a 7.5.",
    )
    estado = models.CharField(
        "Estado",
        max_length=15,
        choices=Estado.choices,
        default=Estado.SANO,
    )
    fecha_reporte = models.DateField(
        "Fecha de último reporte",
        help_text="Fecha de la última modificación del estatus fitosanitario.",
    )
    imagen1 = models.CharField(
        "Imagen 1",
        max_length=500,
        blank=True,
        default="",
        help_text="Ruta relativa URL de la imagen 1.",
    )
    imagen2 = models.CharField(
        "Imagen 2",
        max_length=500,
        blank=True,
        default="",
        help_text="Ruta relativa URL de la imagen 2.",
    )
    imagen3 = models.CharField(
        "Imagen 3",
        max_length=500,
        blank=True,
        default="",
        help_text="Ruta relativa URL de la imagen 3.",
    )
    imagen4 = models.CharField(
        "Imagen 4",
        max_length=500,
        blank=True,
        default="",
        help_text="Ruta relativa URL de la imagen 4.",
    )

    class Meta:
        db_table = "arboles"
        verbose_name = "Árbol"
        verbose_name_plural = "Árboles"
        ordering = ["-fecha_reporte"]

    def __str__(self):
        return f"{self.etiqueta} — {self.especie.nombre}"
