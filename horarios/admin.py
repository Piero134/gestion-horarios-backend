from django.contrib import admin
from .models import Horario

@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('grupo', 'dia', 'hora_inicio', 'hora_fin', 'aula')
    list_filter = ('dia', 'aula')
    search_fields = ('grupo__asignatura__nombre', 'aula__codigo')
