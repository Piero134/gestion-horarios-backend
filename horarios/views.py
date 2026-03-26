from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from horarios.models import Horario
from horarios.serializers import HorarioSerializer
from horarios.filters import HorarioFilter
from escuelas.models import Escuela
from periodos.models import PeriodoAcademico

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

class HorarioPorDiaListView(generics.ListAPIView):
    serializer_class = HorarioSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = HorarioFilter

    def get_escuela(self):
        escuela_id = self.request.query_params.get('escuela')

        if not escuela_id:
            raise ValidationError({"error": "El parámetro 'escuela' es obligatorio."})

        escuela = Escuela.objects.filter(id=escuela_id).first()
        if not escuela:
            raise ValidationError({"error": "Escuela no válida."})

        return escuela

    def get_queryset(self):
        qs = Horario.objects.all()
        escuela = self.get_escuela()

        periodo_id = self.request.query_params.get('periodo')

        qs = qs.filter(
            grupo__asignaturas__plan__escuela=escuela
        ).distinct()

        if periodo_id:
            qs = qs.filter(grupo__periodo_id=periodo_id)
        else:
            periodo_activo = PeriodoAcademico.objects.get_activo()
            qs = qs.filter(grupo__periodo=periodo_activo) if periodo_activo else qs.none()

        return qs.select_related(
            'grupo__asignatura_base',
            'docente',
            'aula'
        ).prefetch_related(
            'grupo__asignaturas_cubiertas',
            'grupo__asignaturas_cubiertas__asignatura',
            'grupo__asignaturas_cubiertas__asignatura__plan'
        ).order_by('hora_inicio')

    def list(self, request, *args, **kwargs):
        ciclo = request.query_params.get('ciclo')
        grupo = request.query_params.get('grupo')

        if not ciclo or not grupo:
            raise ValidationError({
                "error": "Los parámetros 'ciclo' y 'grupo' son obligatorios."
            })

        escuela = self.get_escuela()

        queryset = self.filter_queryset(self.get_queryset())

        queryset = [
            h for h in queryset
            if h.grupo.get_asignatura_para_escuela(escuela).ciclo == int(ciclo)
        ]

        serializer = self.get_serializer(
            queryset,
            many=True,
            context={'escuela': escuela}
        )

        horario_semanal = {
            "Lunes": [], "Martes": [], "Miércoles": [],
            "Jueves": [], "Viernes": [], "Sábado": [], "Domingo": []
        }

        for item in serializer.data:
            dia = item.pop('dia')

            if dia not in horario_semanal:
                horario_semanal[dia] = []

            horario_semanal[dia].append(item)

        # limpiar vacíos
        horario_semanal = {
            dia: clases for dia, clases in horario_semanal.items() if clases
        }

        # ordenar
        for dia in horario_semanal:
            horario_semanal[dia].sort(key=lambda x: x['hora_inicio'])

        return Response(horario_semanal)

@login_required
def horario_asignaturas(request):
    user = request.user

    # Obtenemos las escuelas seguras para este usuario
    escuelas = Escuela.objects.para_usuario(user).order_by('codigo')

    # Por defecto, ciclos del 1 al 10
    ciclos = range(1, 11)
    rol_name = getattr(user.rol, 'name', None) if hasattr(user, 'rol') and user.rol else None

    # Si es de EEGG, limitamos a ciclos 1 y 2
    if rol_name in ["Coordinador de Estudios Generales", "Jefe de Estudios Generales"]:
        ciclos = range(1, 3)

    context = {
        'escuelas': escuelas,
        'ciclos': ciclos,
        'periodos': PeriodoAcademico.objects.all().order_by('-anio', '-fecha_inicio'),
        'periodo_activo': PeriodoAcademico.objects.get_activo(),
    }

    return render(request, 'horarios/horario_asignaturas.html', context)
