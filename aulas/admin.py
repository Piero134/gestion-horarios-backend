from django.contrib import admin
from .models import Aula

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pabellon', 'tipo', 'vacantes', 'facultad', 'activo')
    list_filter = ('pabellon', 'tipo', 'activo', 'facultad')
    search_fields = ('nombre',)
    ordering = ('pabellon', 'nombre')
