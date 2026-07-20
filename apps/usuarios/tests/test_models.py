"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""Tests del modelo Usuario."""

import pytest
from django.db import IntegrityError

from apps.usuarios.models import Usuario


@pytest.mark.django_db
class TestUsuarioModel:
    """Tests para el modelo Usuario."""

    def test_crear_usuario(self, estudiante):
        """Verifica que se crea un usuario con los campos correctos."""
        assert estudiante.matricula == "210001"
        assert estudiante.rol == Usuario.Rol.USER
        assert estudiante.estatus is True
        assert estudiante.grupo == "9A-ISC"
        assert estudiante.cuatrimestre == 9
        assert estudiante.check_password("testpass123")

    def test_str_representation(self, estudiante):
        """Verifica la representación string del usuario."""
        assert "210001" in str(estudiante)
        assert "User" in str(estudiante)

    def test_rol_properties(self, root_user, administrativo, estudiante):
        """Verifica las propiedades de rol."""
        assert root_user.es_root is True
        assert root_user.es_administrativo is True

        assert administrativo.es_root is False
        assert administrativo.es_administrativo is True

        assert estudiante.es_estudiante is True
        assert estudiante.es_administrativo is False

    def test_matricula_unica(self, estudiante):
        """Verifica que no se pueden crear dos usuarios con la misma matrícula."""
        with pytest.raises(IntegrityError):
            Usuario.objects.create_user(
                username="otro",
                matricula="210001",
                password="testpass123",
                rol=Usuario.Rol.USER,
                grupo="9B-ISC",
                cuatrimestre=9,
            )

    def test_uuid_pk(self, estudiante):
        """Verifica que el PK es un UUID."""
        import uuid

        assert isinstance(estudiante.pk, uuid.UUID)
