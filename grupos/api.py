from rest_framework import viewsets
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import GrupoSerializer
from .filters import GrupoFilter
from .utils.exporter import generar_reporte_grupos
from .models import Grupo
from escuelas.models import Escuela
from django.http import HttpResponse
from rest_framework.response import Response

class GrupoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GrupoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = GrupoFilter

    def get_queryset(self):
        user = self.request.user
        escuelas_validas = Escuela.objects.para_usuario(user)
        escuela_id = self.request.query_params.get('escuela')
        rol_name = getattr(user.rol, 'name', None) if hasattr(user, 'rol') and user.rol else None

        if escuela_id and escuelas_validas.filter(id=escuela_id).exists():
            self.escuela_obj = escuelas_validas.get(id=escuela_id)
        else:
            self.escuela_obj = escuelas_validas.first()

        solo_primeros_ciclos = rol_name in [
            'Coordinador de Estudios Generales',
            'Jefe de Estudios Generales'
        ]

        return Grupo.objects.para_escuela(self.escuela_obj, solo_primeros_ciclos)

    def filter_queryset(self, queryset):
        # Filtros Definidos
        queryset = super().filter_queryset(queryset)

        # Optimizacion para N + 1 y ordenamiento
        return queryset.con_info_completa(
        ).order_by(
            '-periodo__anio',
            'asignatura_base__ciclo',
            'asignatura_base__codigo',
            'numero'
        )

    # Acción personalizada para exportar a Excel
    @action(detail=False, methods=['get'])
    def exportar_excel(self, request):
        queryset = self.get_queryset()
        filtro = GrupoFilter(request.GET, queryset=queryset, escuela=self.escuela_obj)

        queryset_final = filtro.qs.con_info_completa()

        resultado = generar_reporte_grupos(queryset_final, request.user, self.escuela_obj)

        # Manejo de errores
        if not resultado:
            return Response(
                {"error": "No se encontraron datos para generar el reporte o no tiene permisos."},
                status=400
            )

        archivo_io, nombre_archivo = resultado

        response = HttpResponse(
            archivo_io,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'

        return response
