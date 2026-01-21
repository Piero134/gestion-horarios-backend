from django.contrib import admin
from .models import Docente, Grupo, Aula, TipoClase, Ciclo, TipoCurso, Curso, Horario

@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    # Columnas que se verán en la lista principal
    list_display = ('id', 'curso', 'docente', 'dia_semana', 'hora_inicio', 'aula')
    
    # Filtros laterales para encontrar datos rápido
    list_filter = ('dia_semana', 'aula', 'docente', 'curso__ciclo')
    
    # Buscador por nombre de curso o docente
    search_fields = ('curso__nombre', 'docente__nombre')

admin.site.register(Docente)
admin.site.register(Grupo)
admin.site.register(Aula)
admin.site.register(TipoCurso)
admin.site.register(Ciclo)
admin.site.register(TipoClase)
admin.site.register(Curso)