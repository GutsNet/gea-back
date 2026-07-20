"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""
Modelo de usuario personalizado para G.E.A.

Extiende AbstractUser para agregar matrícula, rol, grupo, cuatrimestre y estatus.
Los campos grupo y cuatrimestre aplican principalmente a estudiantes.
"""

import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Usuario(AbstractUser):
    """
    Usuario del sistema G.E.A.

    Roles:
        - root: Acceso total al sistema.
        - admin: Valida reportes, gestiona árboles y estudiantes.
        - user: Registra reportes y recolecciones (brigadista).
    """

    class Rol(models.TextChoices):
        ROOT = "root", "Root"
        ADMIN = "admin", "Admin"
        USER = "user", "User"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    matricula = models.CharField(
        "Matrícula",
        max_length=20,
        unique=True,
        help_text="Matrícula institucional de la UTTT.",
    )
    rol = models.CharField(
        "Rol",
        max_length=15,
        choices=Rol.choices,
        default=Rol.USER,
    )
    grupo = models.CharField(
        "Grupo",
        max_length=20,
        default="N/A",
        help_text="Grupo escolar del cuatrimestre vigente.",
    )
    cuatrimestre = models.IntegerField(
        "Cuatrimestre",
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(11)],
        help_text="Período lectivo actual del alumno (1 al 11).",
    )
    estatus = models.BooleanField(
        "Estatus",
        default=True,
        help_text="True = Activo, False = Inactivo.",
    )
    fecha_registro = models.DateField(
        "Fecha de registro",
        auto_now_add=True,
    )
    ultimo_acceso = models.DateTimeField(
        "Último acceso",
        null=True,
        blank=True,
    )

    # Usar matrícula como campo de login en lugar de username
    USERNAME_FIELD = "matricula"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "usuarios"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["-fecha_registro"]

    def __str__(self):
        return f"{self.matricula} ({self.get_rol_display()})"

    @property
    def es_root(self):
        return self.rol == self.Rol.ROOT

    @property
    def es_administrativo(self):
        return self.rol in (self.Rol.ROOT, self.Rol.ADMIN)

    @property
    def es_estudiante(self):
        return self.rol == self.Rol.USER
