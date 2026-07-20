"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""Views del módulo de usuarios y autenticación."""

from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdministrativo, IsRoot

from .models import Usuario
from .serializers import (
    LoginSerializer,
    PerfilSerializer,
    TokenResponseSerializer,
    UsuarioCreateSerializer,
    UsuarioSerializer,
)
from .services import registrar_acceso


class LoginView(APIView):
    """
    POST /api/v1/auth/login/

    Autentica por matrícula + contraseña, retorna tokens JWT + datos del usuario.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        registrar_acceso(user)

        response_data = TokenResponseSerializer.from_user(user)
        return Response(response_data, status=status.HTTP_200_OK)


class PerfilView(generics.RetrieveUpdateAPIView):
    """
    GET/PATCH /api/v1/auth/perfil/

    Ver o actualizar el perfil del usuario autenticado.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UsuarioSerializer
        return PerfilSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    CRUD /api/v1/auth/usuarios/

    Solo accesible por Root. Administrativos pueden listar.
    Soporta filtro por rol para obtener solo estudiantes:
        GET /api/v1/auth/usuarios/?rol=user
    """

    queryset = Usuario.objects.all()
    filterset_fields = ["rol", "estatus", "grupo", "cuatrimestre"]
    search_fields = ["matricula", "username"]
    ordering_fields = ["fecha_registro", "matricula", "ultimo_acceso"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsRoot()]
        return [IsAuthenticated(), IsAdministrativo()]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return UsuarioCreateSerializer
        return UsuarioSerializer
