from rest_framework import serializers
from .models import PlanEstudios
from asignaturas.models import Asignatura

class AsignaturaSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    prerequisitos = serializers.StringRelatedField(many=True)

    class Meta:
        model = Asignatura
        fields = [
            'id', 'codigo', 'nombre', 'tipo', 'tipo_display', 'creditos',
            'ciclo', 'prerequisitos', 'horas_teoria', 'horas_practica', 'horas_laboratorio'
        ]

class PlanSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanEstudios
        fields = ['id', 'anio']



class PlanDetalleSerializer(serializers.ModelSerializer):
    escuela_nombre = serializers.ReadOnlyField(source='escuela.nombre')
    facultad_siglas = serializers.ReadOnlyField(source='escuela.facultad.siglas')
    asignaturas = AsignaturaSerializer(many=True, read_only=True)

    class Meta:
        model = PlanEstudios
        fields = ['id', 'anio', 'escuela_nombre', 'facultad_siglas', 'asignaturas']
