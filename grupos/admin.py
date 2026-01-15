from django.contrib import admin
from .models import Grupo
from horarios.admin import HorarioInline

@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ('asignatura', 'nombre', 'periodo', 'docente', 'cupo_maximo')
    list_filter = ('periodo__activo', 'periodo', 'asignatura__plan')
    search_fields = ('asignatura__nombre', 'docente__apellido', 'nombre')
    autocomplete_fields = ['asignatura', 'docente'] # Rapidez de búsqueda
    inlines = [HorarioInline] # Para gestionar el tiempo y espacio aquí mismo
