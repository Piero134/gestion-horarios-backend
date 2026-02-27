from rest_framework import serializers

# --- IMPORTS DE LOS MODELOS POR APP ---
from horarios.models import Horario
from aulas.models import Aula
from grupos.models import Grupo
from periodos.models import PeriodoAcademico
from asignaturas.models import Asignatura
from docentes.models import Docente

# Los serializadores de Periodo, Asignatura, Docente y Aula se mantienen por si los usas en otras vistas
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
        fields = ['id', 'codigo', 'nombre', 'ciclo', 'tipo', 'creditos', 'horas_teoria', 'horas_practica', 'horas_laboratorio', 'plan_id', 'escuela']

class DocenteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.ReadOnlyField()
    class Meta:
        model = Docente
        fields = ['id', 'nombres', 'apellido_paterno', 'apellido_materno', 'nombre_completo', 'email']

# --- SERIALIZER PRINCIPAL PARA LA APP MÓVIL ---
class ClaseSerializer(serializers.ModelSerializer):
    """Estructura de la clase individual formateada para móvil"""
    curso = serializers.SerializerMethodField()
    docente = serializers.SerializerMethodField()
    aula = serializers.SerializerMethodField()
    tipo_clase = serializers.SerializerMethodField()
    hora_inicio = serializers.TimeField(format="%H:%M")
    hora_fin = serializers.TimeField(format="%H:%M")

    class Meta:
        model = Horario
        fields = ['curso', 'docente', 'aula', 'tipo_clase', 'hora_inicio', 'hora_fin']

    def get_curso(self, obj):
        # Nombre del curso en MAYÚSCULAS
        return obj.grupo.asignatura.nombre.upper() if obj.grupo and obj.grupo.asignatura else ""

    def get_docente(self, obj):
        # Docente en MAYÚSCULAS (Apellidos + Nombres)
        if obj.docente:
            return f"{obj.docente.apellido_paterno} {obj.docente.apellido_materno} {obj.docente.nombres}".upper()
        return "SIN ASIGNAR"

    def get_aula(self, obj):
        # RETORNA SIEMPRE STRING: El nombre del aula o "0"
        if obj.aula:
            return str(obj.aula.nombre)
        return "0"

    def get_tipo_clase(self, obj):
        # Mapeo de tipos sin tildes para el requerimiento móvil
        mapping = {'T': 'Teoria', 'P': 'Practica', 'L': 'Laboratorio'}
        return mapping.get(obj.tipo, 'Teoria')

# Serializer antiguo mantenido por compatibilidad
class GrupoCustomSerializer(serializers.ModelSerializer):
    grupo_id = serializers.IntegerField(source='id', read_only=True)
    numero = serializers.IntegerField(read_only=True)
    asignatura = serializers.CharField(source='asignatura.nombre', read_only=True)
    periodo_detalle = PeriodoSerializer(source='periodo', read_only=True)
    horarios = serializers.SerializerMethodField()
    class Meta:
        model = Grupo
        fields = ['grupo_id', 'numero', 'asignatura', 'periodo_detalle', 'horarios']
    def get_horarios(self, obj):
        qs = obj.horarios.all().select_related('aula', 'docente', 'grupo__asignatura').order_by('hora_inicio')
        dias_mapping = {1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 5: 'Viernes', 6: 'Sábado', 7: 'Domingo'}
        lista_dias = []
        for dia_id, dia_nombre in dias_mapping.items():
            clases = [h for h in qs if h.dia == dia_id]
            if clases:
                lista_dias.append({"dia": dia_nombre, "clases": ClaseSerializer(clases, many=True).data})
        return [{"dias": lista_dias}] if lista_dias else []