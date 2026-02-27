from rest_framework import serializers
from .models import Horario

class ClaseSerializer(serializers.ModelSerializer):
    """
    Serializador individual para cada bloque de clase.
    Extrae la información relacionada de Asignatura, Docente y Aula.
    """
    # Extraemos el nombre del curso navegando por la relación: Horario -> Grupo -> Asignatura
    curso = serializers.CharField(source='grupo.asignatura.nombre', read_only=True)
    docente = serializers.SerializerMethodField()
    aula = serializers.SerializerMethodField()
    # get_tipo_display es un método nativo de Django para campos con choices (T, P, L)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    hora_inicio = serializers.TimeField(format="%H:%M")
    hora_fin = serializers.TimeField(format="%H:%M")

    class Meta:
        model = Horario
        fields = ['curso', 'docente', 'aula', 'tipo_display', 'hora_inicio', 'hora_fin']

    def get_docente(self, obj):
        # Usamos la property 'nombre_completo' que ya definiste en tu modelo Docente
        if obj.docente:
            return obj.docente.nombre_completo
        return "Es none"

    def get_aula(self, obj):
        # Extraemos el nombre del aula o devolvemos el texto por defecto
        if obj.aula:
            return obj.aula.nombre
        return "Es none"