"""Lógica de negocio del módulo de usuarios."""

from django.utils import timezone


def registrar_acceso(usuario):
    """Actualiza el timestamp de último acceso del usuario."""
    usuario.ultimo_acceso = timezone.now()
    usuario.save(update_fields=["ultimo_acceso"])
