from rest_framework import serializers

# --- IMPORTS DE LOS MODELOS POR APP ---
from horarios.models import Horario
from aulas.models import Aula
from grupos.models import Grupo
from periodos.models import PeriodoAcademico
from asignaturas.models import Asignatura
from docentes.models import Docente


class PeriodoSerializer(serializers.ModelSerializer):
    activo = serializers.ReadOnlyField()

    class Meta:
        model = PeriodoAcademico
        fields = ['id', 'nombre', 'tipo', 'anio', 'fecha_inicio', 'fecha_fin', 'activo']


class AsignaturaSerializer(serializers.ModelSerializer):
    plan_id = serializers.PrimaryKeyRelatedField(source='plan', read_only=True)
    escuela = serializers.CharField(source='plan.escuela.nombre', default=None, read_only=True)

    class Meta:
        model = Asignatura
        fields = [
            'id', 'codigo', 'nombre', 'ciclo', 'tipo', 'creditos', 
            'horas_teoria', 'horas_practica', 'horas_laboratorio', 
            'plan_id', 'escuela'
        ]


class DocenteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.ReadOnlyField()

    class Meta:
        model = Docente
        fields = ['id', 'nombres', 'apellido_paterno', 'apellido_materno', 'nombre_completo', 'email']


class AulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aula
        fields = ['id', 'nombre', 'capacidad', 'es_laboratorio']


class ClaseSerializer(serializers.ModelSerializer):
    """Estructura de la clase individual para el detalle del horario"""
    curso = serializers.CharField(source='grupo.asignatura.nombre', read_only=True)
    docente = serializers.SerializerMethodField()
    aula = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    hora_inicio = serializers.TimeField(format="%H:%M")
    hora_fin = serializers.TimeField(format="%H:%M")

    class Meta:
        model = Horario
        fields = ['curso', 'docente', 'aula', 'tipo_display', 'hora_inicio', 'hora_fin']

    def get_docente(self, obj):
        # Extrae el docente directamente del modelo Horario
        doc = obj.docente
        return doc.nombre_completo if doc else "Sin docente asignado"

    def get_aula(self, obj):
        return obj.aula.nombre if obj.aula else "Sin aula asignada"


class GrupoCustomSerializer(serializers.ModelSerializer):
    """Serializer principal que agrupa los horarios por día"""
    grupo_id = serializers.IntegerField(source='id', read_only=True)
    numero = serializers.IntegerField(read_only=True)
    asignatura = serializers.CharField(source='asignatura.nombre', read_only=True)
    periodo_detalle = PeriodoSerializer(source='periodo', read_only=True)
    horarios = serializers.SerializerMethodField()

    class Meta:
        model = Grupo
        fields = ['grupo_id', 'numero', 'asignatura', 'periodo_detalle', 'horarios']

    def get_horarios(self, obj):
        qs = obj.horarios.all().select_related(
            'aula', 'docente', 'grupo__asignatura'
        ).order_by('hora_inicio')
        
        dias_mapping = {
            1: 'Lunes', 2: 'Martes', 3: 'Miércoles',
            4: 'Jueves', 5: 'Viernes', 6: 'Sábado', 7: 'Domingo'
        }

        lista_dias = []
        for dia_id, dia_nombre in dias_mapping.items():
            clases = [h for h in qs if h.dia == dia_id]
            if clases:
                lista_dias.append({
                    "dia": dia_nombre,
                    "clases": ClaseSerializer(clases, many=True).data
                })

        return [{"dias": lista_dias}] if lista_dias else []