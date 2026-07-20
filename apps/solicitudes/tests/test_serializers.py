import pytest
from rest_framework.test import APIRequestFactory

from apps.arboles.models import Ubicacion
from apps.solicitudes.serializers import SolicitudCreateSerializer
from apps.usuarios.models import Usuario


@pytest.mark.django_db
class TestSolicitudCreateSerializer:
    def test_serializer_returns_id_after_create(self):
        user = Usuario.objects.create_user(
            username="estudiante-test",
            matricula="EST-001",
            password="testpass123",
            rol=Usuario.Rol.USER,
            grupo="9A-ISC",
            cuatrimestre=9,
        )
        ubicacion = Ubicacion.objects.create(
            nombre="Ubicacion-TEST-001",
            coordenadas="test-coords-001",
        )

        factory = APIRequestFactory()
        request = factory.post("/api/v1/solicitudes/")
        request.user = user

        serializer = SolicitudCreateSerializer(
            data={
                "especie_existente": None,
                "nueva_especie_nombre": "Pino Nuevo",
                "nueva_especie_nombre_cientifico": "Pinus nuevo",
                "nueva_especie_nativa": False,
                "arbol_existente": None,
                "nueva_etiqueta": "ARB-TEST-001",
                "id_area": ubicacion.id,
                "coordenadas_exactas": "19.5466,-99.4568",
                "n1": 2.5,
                "n2": 2.0,
                "n3": 1.5,
                "observaciones": "Solicitud de prueba completa",
                "imagen1": "",
                "imagen2": "",
                "imagen3": "",
                "imagen4": "",
            },
            context={"request": request},
        )

        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()

        assert instance.id is not None
        assert instance.coordenadas_exactas == "19.5466,-99.4568"
        assert "id" in serializer.data
        assert serializer.data["id"] == str(instance.id)
        assert serializer.data["coordenadas_exactas"] == "19.5466,-99.4568"
