from rest_framework import serializers
from grupos.models import Grupo
from horarios.models import Horario

class HorarioSerializer(serializers.ModelSerializer):
    dia_nombre = serializers.CharField(source='get_dia_display')
    docente_nombre = serializers.CharField(source='docente.__str__', read_only=True)
    aula_nombre = serializers.CharField(source='aula.nombre', read_only=True, default="-")

    class Meta:
        model = Horario
        fields = ['dia_nombre', 'hora_inicio', 'hora_fin', 'tipo', 'docente_nombre', 'aula_nombre']

class GrupoSerializer(serializers.ModelSerializer):
    asignatura = serializers.CharField(source='asignatura.nombre')
    codigo = serializers.CharField(source='asignatura.codigo')
    ciclo = serializers.IntegerField(source='asignatura.ciclo')
    plan = serializers.CharField(source='asignatura.plan.nombre')
    horarios = HorarioSerializer(many=True, read_only=True)
    #vacantes = serializers.IntegerField(source='total_vacantes')

    class Meta:
        model = Grupo
        fields = ['id', 'numero', 'codigo', 'asignatura', 'ciclo', 'plan', 'horarios']
