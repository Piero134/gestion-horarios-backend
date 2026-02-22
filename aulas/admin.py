from django.contrib import admin
from .models import Aula

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    # Solo campos que EXISTEN en tu nuevo modelo
    list_display = ('nombre', 'pabellon', 'vacantes', 'tipo_sesion', 'facultad')
    list_filter = ('pabellon', 'tipo_sesion', 'facultad')
    search_fields = ('nombre',)