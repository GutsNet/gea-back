"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

from django.apps import AppConfig


class ArbolesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.arboles"
    verbose_name = "Árboles"
