"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""Fixtures compartidas para tests del módulo de usuarios."""

import pytest

from apps.usuarios.models import Usuario


@pytest.fixture
def root_user(db):
    """Crea un usuario Root."""
    return Usuario.objects.create_user(
        username="root",
        matricula="ROOT-001",
        password="testpass123",
        rol=Usuario.Rol.ROOT,
        grupo="N/A",
        cuatrimestre=1,
    )


@pytest.fixture
def administrativo(db):
    """Crea un usuario Administrativo."""
    return Usuario.objects.create_user(
        username="admin",
        matricula="ADM-001",
        password="testpass123",
        rol=Usuario.Rol.ADMIN,
        grupo="N/A",
        cuatrimestre=1,
    )


@pytest.fixture
def estudiante(db):
    """Crea un usuario Estudiante."""
    return Usuario.objects.create_user(
        username="estudiante",
        matricula="210001",
        password="testpass123",
        rol=Usuario.Rol.USER,
        grupo="9A-ISC",
        cuatrimestre=9,
    )
