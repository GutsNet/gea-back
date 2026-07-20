"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""Permisos personalizados basados en roles del sistema G.E.A."""

from rest_framework.permissions import BasePermission


class IsRoot(BasePermission):
    """Permite acceso solo a usuarios con rol Root."""

    message = "Solo los administradores del sistema pueden realizar esta acción."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol == "root"
        )


class IsAdministrativo(BasePermission):
    """Permite acceso a administrativos y Root."""

    message = "Solo administrativos o Root pueden realizar esta acción."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol in ("admin", "root")
        )


class IsEstudiante(BasePermission):
    """Permite acceso a estudiantes, administrativos y Root."""

    message = "Acceso restringido a usuarios del sistema."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol in ("user", "admin", "root")
        )


class IsOwnerOrAdministrativo(BasePermission):
    """
    Permite acceso al recurso si el usuario es el dueño del objeto
    o es administrativo/Root.
    """

    message = "Solo puedes acceder a tus propios recursos o ser administrativo."

    def has_object_permission(self, request, view, obj):
        if request.user.rol in ("admin", "root"):
            return True

        # Check common owner fields
        for field in ("responsable", "usuario"):
            if hasattr(obj, field):
                return getattr(obj, field) == request.user

        return False
