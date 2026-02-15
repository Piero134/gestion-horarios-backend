from django.contrib import admin
from .models import Facultad, Departamento

@admin.register(Facultad)
class FacultadAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'siglas',
        'nombre',
    )

    list_display_links = ('nombre',)

    search_fields = (
        'codigo',
        'siglas',
        'nombre',
    )

    ordering = ('codigo',)

    fieldsets = (
        (None, {
            'fields': ('codigo', 'siglas', 'nombre')
        }),
    )

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'facultad',
    )

    list_display_links = ('nombre',)

    search_fields = (
        'nombre',
        'facultad__nombre',
    )

    ordering = ('nombre',)

    fieldsets = (
        (None, {
            'fields': ('nombre', 'facultad')
        }),
    )
