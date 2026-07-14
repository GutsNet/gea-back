import pytest
from django.utils import timezone

from apps.arboles.models import Arbol, Especie, Ubicacion
from apps.arboles.services import recalcular_infestacion
from apps.reportes.models import Reporte
from apps.usuarios.models import Usuario


@pytest.mark.django_db
class TestReporteModel:
    def test_nivel_infestacion_promedio_es_suma_de_los_tres_niveles(self):
        especie = Especie.objects.create(
            nombre="Pino",
            nombre_cientifico="Pinus sp.",
            nativa=False,
        )
        ubicacion = Ubicacion.objects.create(coordenadas="test-coords")
        usuario = Usuario.objects.create_user(
            username="brigadista",
            matricula="BRI-001",
            password="testpass123",
            rol=Usuario.Rol.ESTUDIANTE,
            grupo="9A-ISC",
            cuatrimestre=9,
        )
        arbol = Arbol.objects.create(
            especie=especie,
            id_area=ubicacion,
            etiqueta="ARB-001",
            nivel_infestacion=0.0,
            estado=Arbol.Estado.INFESTADO,
            fecha_reporte=timezone.localdate(),
        )
        reporte = Reporte.objects.create(
            id_arbol=arbol,
            responsable=usuario,
            n1=2.5,
            n2=2.5,
            n3=2.5,
            status_reporte=Reporte.StatusReporte.VALIDADO,
            hora=timezone.now(),
            observaciones="",
        )

        assert reporte.nivel_infestacion_promedio == 7.5

        recalcular_infestacion(arbol)

        arbol.refresh_from_db()
        assert arbol.nivel_infestacion == 7.5
