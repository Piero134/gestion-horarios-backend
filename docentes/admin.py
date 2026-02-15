from django.contrib import admin
from .models import Docente

@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ('dni', '__str__', 'tipo', 'ver_codigo_o_dni', 'departamento')
    list_filter = ('tipo', 'categoria', 'dedicacion')
    search_fields = ('apellido_paterno', 'apellido_materno', 'nombres', 'dni', 'codigo')

    # Organizar campos por secciones
    fieldsets = (
        ('Datos Personales', {
            'fields': ('tipo', 'dni', 'apellido_paterno', 'apellido_materno', 'nombres', 'email', 'departamento')
        }),
        ('Datos Académicos (Solo Nombrados)', {
            'fields': ('codigo', 'categoria', 'dedicacion'),
            'classes': ('collapse',), # Opcional: hace que esta sección sea colapsable
            'description': 'Estos campos son obligatorios si el tipo es "Nombrado".'
        }),
    )

    def ver_codigo_o_dni(self, obj):
        return obj.codigo if obj.codigo else "DNI: " + obj.dni
    ver_codigo_o_dni.short_description = "ID / Código"
