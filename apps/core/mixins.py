"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""Mixins reutilizables para modelos del proyecto."""

from django.db import models


class TimestampMixin(models.Model):
    """
    Mixin que agrega campos created_at y updated_at a cualquier modelo.
    """

    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Última actualización", auto_now=True)

    class Meta:
        abstract = True
