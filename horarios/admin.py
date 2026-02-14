from django.contrib import admin
from .models import Horario

@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('grupo', 'dia', 'hora_inicio', 'hora_fin', 'tipo', 'aula', 'docente')
    list_filter = ('dia', 'aula', 'tipo', 'grupo__periodo')

    search_fields = (
        'grupo__asignatura__nombre', # Buscar por nombre de curso
        'aula__codigo',              # Buscar por aula
        'docente__nombre',           # Buscar por nombre profe
        'docente__apellido'          # Buscar por apellido profe
    )

    autocomplete_fields = ['grupo', 'aula', 'docente']

    # Ordenar por defecto
    ordering = ['dia', 'hora_inicio']
