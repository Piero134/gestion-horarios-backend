from django.contrib import admin
from .models import Grupo
from horarios.models import Horario

class HorarioInline(admin.TabularInline):
    model = Horario
    extra = 1
    autocomplete_fields = ['aula']

@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ('asignatura', 'nombre', 'periodo', 'docente')
    list_filter = ('periodo', 'asignatura__plan')
    search_fields = ('asignatura__nombre', 'docente__apellido', 'nombre')
    autocomplete_fields = ['asignatura', 'docente'] # Rapidez de búsqueda
    inlines = [HorarioInline] # Para gestionar el tiempo y espacio aquí mismo
