from rest_framework import serializers
from grupos.models import Grupo
from horarios.serializers import HorarioSerializer

class GrupoSerializer(serializers.ModelSerializer):
    asignatura = serializers.CharField(source='asignatura.nombre')
    codigo = serializers.CharField(source='asignatura.codigo')
    ciclo = serializers.IntegerField(source='asignatura.ciclo')
    horarios = HorarioSerializer(many=True, read_only=True)
    #vacantes = serializers.IntegerField(source='total_vacantes')

    class Meta:
        model = Grupo
        fields = ['id', 'numero', 'codigo', 'asignatura', 'ciclo', 'horarios']
