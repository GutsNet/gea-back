"""Serializers para el módulo de usuarios y autenticación."""

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer completo de usuario (lectura)."""

    class Meta:
        model = Usuario
        fields = [
            "id",
            "matricula",
            "rol",
            "grupo",
            "cuatrimestre",
            "estatus",
            "fecha_registro",
            "ultimo_acceso",
        ]
        read_only_fields = ["id", "fecha_registro", "ultimo_acceso"]


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios (Root only)."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = [
            "matricula",
            "username",
            "password",
            "rol",
            "grupo",
            "cuatrimestre",
            "estatus",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario


class LoginSerializer(serializers.Serializer):
    """Serializer para login por matrícula + contraseña."""

    matricula = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            request=self.context.get("request"),
            username=data["matricula"],  # USERNAME_FIELD = matricula
            password=data["password"],
        )
        if not user:
            raise serializers.ValidationError("Matrícula o contraseña incorrectos.")
        if not user.estatus:
            raise serializers.ValidationError("Tu cuenta está desactivada.")
        data["user"] = user
        return data


class TokenResponseSerializer(serializers.Serializer):
    """Serializer de respuesta con tokens JWT y datos del usuario."""

    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UsuarioSerializer()

    @classmethod
    def from_user(cls, user):
        """Genera tokens y construye la respuesta."""
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UsuarioSerializer(user).data,
        }


class PerfilSerializer(serializers.ModelSerializer):
    """Serializer para que el usuario edite su propio perfil."""

    class Meta:
        model = Usuario
        fields = ["grupo", "cuatrimestre"]
