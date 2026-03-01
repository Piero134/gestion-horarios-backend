from rest_framework import serializers
from horarios.models import Horario

class HorarioSerializer(serializers.ModelSerializer):
    dia = serializers.CharField(source='get_dia_display')
    tipo = serializers.CharField(source='get_tipo_display')
    docente = serializers.SerializerMethodField(read_only=True)
    aula = serializers.SerializerMethodField(read_only=True)
    hora_inicio = serializers.TimeField(format="%H:%M")
    hora_fin = serializers.TimeField(format="%H:%M")

    def get_docente(self, obj):
        if obj.docente:
            return str(obj.docente)
        return "SIN ASIGNAR"

    def get_aula(self, obj):
        if obj.aula:
            return f"{obj.aula.nombre} - {obj.aula.pabellon}"
        return "-"

    class Meta:
        model = Horario
        fields = ['dia', 'hora_inicio', 'hora_fin', 'tipo', 'docente', 'aula']

class HorarioDetalleSerializer(HorarioSerializer):
    curso = serializers.CharField(source='grupo.asignatura.nombre', read_only=True)

    class Meta(HorarioSerializer.Meta):
        # Sumamos curso a los campos originales
        fields = ['curso'] + HorarioSerializer.Meta.fields
