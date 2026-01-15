from django.contrib import admin
from .models import PeriodoAcademico

@admin.register(PeriodoAcademico)
class PeriodoAcademicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'anio', 'fecha_inicio', 'fecha_fin', 'activo')
    list_filter = ('tipo', 'anio', 'activo')
    search_fields = ('nombre',)
    list_editable = ('activo',) # Puedes activar/desactivar periodos desde la lista principal
