from rest_framework import serializers
from horarios.models import Horario

class HorarioSerializer(serializers.ModelSerializer):
    dia = serializers.CharField(source='get_dia_display')
    tipo = serializers.CharField(source='get_tipo_display')
    docente = serializers.SerializerMethodField()
    aula = serializers.SerializerMethodField()
    curso = serializers.SerializerMethodField()
    codigo = serializers.SerializerMethodField()
    ciclo = serializers.SerializerMethodField()

    hora_inicio = serializers.TimeField(format="%H:%M")
    hora_fin = serializers.TimeField(format="%H:%M")

    def get_docente(self, obj):
        return str(obj.docente) if obj.docente else "SIN ASIGNAR"

    def get_aula(self, obj):
        return f"{obj.aula.nombre} - {obj.aula.pabellon}" if obj.aula else "-"

    def get_asignatura(self, obj):
        escuela = self.context.get('escuela')
        return obj.grupo.get_asignatura_para_escuela(escuela)

    def get_curso(self, obj):
        return self.get_asignatura(obj).nombre

    def get_codigo(self, obj):
        return self.get_asignatura(obj).codigo

    def get_ciclo(self, obj):
        return self.get_asignatura(obj).ciclo

    class Meta:
        model = Horario
        fields = [
            'curso', 'codigo', 'ciclo',
            'dia', 'hora_inicio', 'hora_fin',
            'tipo', 'docente', 'aula'
        ]
