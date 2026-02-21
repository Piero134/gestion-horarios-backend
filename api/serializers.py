from rest_framework import serializers

# IMPORTAMOS DESDE LAS APPS ORIGINALES
from grupos.models import Grupo
from horarios.models import Horario

class ClaseSerializer(serializers.ModelSerializer):
    # Accedemos a relaciones profundas (Grupo -> Asignatura -> Nombre)
    curso = serializers.CharField(source='grupo.asignatura.nombre', read_only=True)
    docente = serializers.SerializerMethodField()
    aula = serializers.SerializerMethodField()
    
    # Formato de hora limpio (HH:MM)
    hora_inicio = serializers.TimeField(format="%H:%M")
    hora_fin = serializers.TimeField(format="%H:%M")

    class Meta:
        model = Horario # Usamos el modelo de la app 'horarios'
        fields = ['curso', 'docente', 'aula', 'hora_inicio', 'hora_fin']

    def get_docente(self, obj):
        # Lógica para replicar "Es none" si no hay docente
        return str(obj.grupo.docente) if obj.grupo.docente else "Es none"

    def get_aula(self, obj):
        # Lógica para replicar "Es none" si no hay aula
        return obj.aula.nombre if obj.aula else "Es none"

class GrupoCustomSerializer(serializers.ModelSerializer):
    grupo = serializers.CharField(source='id', read_only=True)
    horarios = serializers.SerializerMethodField()

    class Meta:
        model = Grupo 
        fields = ['grupo', 'horarios']

    def get_horarios(self, obj):
        qs = obj.horarios.all().order_by('hora_inicio')
        
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

        if not lista_dias:
            return []

        return [{"dias": lista_dias}]