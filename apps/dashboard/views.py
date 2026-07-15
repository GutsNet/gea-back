"""
G.E.A. Backend
Autor: Gael Landa
Proyecto: G.E.A. (Gestión Ecológica Arbórea)
"""

"""
Views del dashboard — endpoints agregados para KPIs y visualizaciones.

Estos endpoints alimentan el dashboard del frontend (ApexCharts)
y el mapa del campus (Leaflet).
"""

from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncMonth
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.arboles.models import Arbol, Especie
from apps.recoleccion.models import Recoleccion
from apps.reportes.models import Reporte
from apps.usuarios.models import Usuario


class ResumenView(APIView):
    """
    GET /api/v1/dashboard/resumen/

    KPIs generales del sistema:
    - Total de árboles por estado
    - Total de reportes por status
    - Kg recolectados
    - Estudiantes activos
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        arboles_stats = Arbol.objects.aggregate(
            total=Count("id"),
            sanos=Count("id", filter=Q(estado="Sano")),
            infestados=Count("id", filter=Q(estado="Infestado")),
            en_limpieza=Count("id", filter=Q(estado="Limpieza")),
            saneados=Count("id", filter=Q(estado="Saneado")),
        )

        reportes_stats = Reporte.objects.aggregate(
            total=Count("id"),
            validados=Count("id", filter=Q(status_reporte="Validado")),
            rechazados=Count("id", filter=Q(status_reporte="Rechazado")),
        )

        kg_total = Recoleccion.objects.aggregate(total=Sum("kilos"))["total"] or 0

        estudiantes_activos = Usuario.objects.filter(
            rol="Estudiante", estatus=True
        ).count()

        return Response(
            {
                "arboles": arboles_stats,
                "reportes": reportes_stats,
                "kg_recolectados": float(kg_total),
                "estudiantes_activos": estudiantes_activos,
            }
        )


class EvolucionReportesView(APIView):
    """
    GET /api/v1/dashboard/evolucion-reportes/

    Serie temporal de reportes agrupados por mes.
    Diseñado para alimentar un gráfico de líneas/barras en ApexCharts.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        datos = (
            Reporte.objects.annotate(mes=TruncMonth("hora"))
            .values("mes")
            .annotate(
                total=Count("id"),
                validados=Count("id", filter=Q(status_reporte="Validado")),
                rechazados=Count("id", filter=Q(status_reporte="Rechazado")),
            )
            .order_by("mes")
        )

        return Response(list(datos))


class MapaCalorView(APIView):
    """
    GET /api/v1/dashboard/mapa-calor/

    Árboles con sus coordenadas (via Ubicación) y nivel de infestación.
    Diseñado para alimentar un mapa de calor en Leaflet.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        arboles = (
            Arbol.objects.select_related("id_area", "especie")
            .values(
                "etiqueta",
                "nivel_infestacion",
                "estado",
                "especie__nombre",
                "id_area__coordenadas",
            )
        )

        return Response(list(arboles))


class EspeciesAfectadasView(APIView):
    """
    GET /api/v1/dashboard/especies-afectadas/

    Ranking de especies por cantidad de árboles con infestación.
    Diseñado para un gráfico de barras/pie en ApexCharts.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        datos = (
            Especie.objects.annotate(
                total_arboles=Count("arboles"),
                arboles_infestados=Count(
                    "arboles",
                    filter=Q(arboles__estado="Infestado"),
                ),
                nivel_promedio=Avg("arboles__nivel_infestacion"),
            )
            .filter(total_arboles__gt=0)
            .values("nombre", "nombre_cientifico", "total_arboles", "arboles_infestados", "nivel_promedio")
            .order_by("-arboles_infestados")
        )

        return Response(list(datos))
