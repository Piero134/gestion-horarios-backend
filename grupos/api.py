from rest_framework import viewsets
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import GrupoSerializer
from .filters import GrupoFilter
from .utils.exporter import generar_reporte_grupos
from .models import Grupo
from periodos.models import PeriodoAcademico
from django.http import HttpResponse
from rest_framework.response import Response

class GrupoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GrupoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = GrupoFilter

    def get_queryset(self):
        user = self.request.user
        queryset = Grupo.objects.para_usuario(user).select_related(
            'periodo', 'asignatura__plan__escuela__facultad'
        )

        periodo_id = self.request.query_params.get('periodo')
        if not periodo_id:
            periodo_activo = PeriodoAcademico.objects.get_activo()
            if periodo_activo:
                queryset = queryset.filter(periodo=periodo_activo)

        return queryset

    def filter_queryset(self, queryset):
        # Filtros Definidos
        queryset = super().filter_queryset(queryset)

        # Optimizacion para N + 1 y ordenamiento
        return queryset.con_info_completa().prefetch_related(
            'horarios__docente', 'horarios__aula'
        ).order_by(
            '-periodo__anio',
            'asignatura__ciclo',
            'asignatura__codigo',
            'numero'
        )
