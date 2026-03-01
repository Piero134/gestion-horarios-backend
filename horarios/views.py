from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from horarios.models import Horario
from horarios.serializers import HorarioDetalleSerializer
from horarios.filters import HorarioFilter
from escuelas.models import Escuela
from periodos.models import PeriodoAcademico

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

class HorarioPorDiaListView(generics.ListAPIView):
    queryset = Horario.objects.all()
    serializer_class = HorarioDetalleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = HorarioFilter

    def get_queryset(self):
        qs = Horario.objects.para_usuario(self.request.user)

        return qs.select_related(
            'grupo__asignatura', 'docente', 'aula'
        ).order_by('hora_inicio')

    def list(self, request, *args, **kwargs):
        # Validacion de parametros obligatorios
        ciclo_param = request.query_params.get('ciclo')
        grupo_param = request.query_params.get('grupo')
        escuela_param = request.query_params.get('escuela')
        periodo_param = request.query_params.get('periodo')

        if not ciclo_param or not grupo_param:
            raise ValidationError({
                "error": "Los parámetros 'ciclo' y 'grupo' son estrictamente obligatorios."
            })

        # DRF filtra y serializa los datos automaticamente
        qs = self.get_queryset()

        if not periodo_param:
            periodo_activo = PeriodoAcademico.objects.get_activo()
            if periodo_activo:
                qs = qs.filter(grupo__periodo=periodo_activo)
            else:
                # Si no envían periodo y tampoco hay uno activo, devolvemos vacío
                qs = qs.none()

        if not escuela_param:
            escuelas_permitidas = Escuela.objects.para_usuario(request.user)

            if escuelas_permitidas.count() == 1:
                qs = qs.filter(grupo__asignatura__plan__escuela=escuelas_permitidas.first())
            else:
                raise ValidationError({
                    "error": "El parámetro 'escuela' es obligatorio para tu rol, por favor especifícalo."
                })

        queryset = self.filter_queryset(qs)
        serializer = self.get_serializer(queryset, many=True)

        horario_semanal = {
            "Lunes": [], "Martes": [], "Miércoles": [],
            "Jueves": [], "Viernes": [], "Sábado": [], "Domingo": []
        }

        for item in serializer.data:
            # Extraemos el dia
            dia = item.pop('dia')

            if dia in horario_semanal:
                horario_semanal[dia].append(item)
            else:
                # En caso de que el día no esté en el diccionario (lo cual no debería pasar), lo agregamos
                horario_semanal[dia] = [item]

        # Limpiamos dias sin clases
        horario_semanal = {dia: clases for dia, clases in horario_semanal.items() if clases}

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
