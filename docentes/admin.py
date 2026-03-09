from django.contrib import admin
from .models import Docente

@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ('obtener_nombre_completo', 'dni', 'tipo', 'facultad', 'departamento', 'codigo', 'activo')

    list_filter = ('activo', 'tipo', 'facultad', 'departamento', 'categoria', 'dedicacion')

    search_fields = ('apellido_paterno', 'apellido_materno', 'nombres', 'dni', 'codigo', 'email')

    fieldsets = (
        ('Datos Personales', {
            'fields': ('dni', 'apellido_paterno', 'apellido_materno', 'nombres', 'email')
        }),
        ('Datos Institucionales', {
            'fields': ('activo', 'tipo', 'facultad', 'departamento')
        }),
        ('Datos Académicos (Solo Nombrados)', {
            'fields': ('codigo', 'categoria', 'dedicacion'),
            'classes': ('collapse',),
            'description': 'Estos campos son obligatorios si el tipo de docente es "Nombrado". Si es "Contratado", se limpiarán automáticamente.'
        }),
    )

    def obtener_nombre_completo(self, obj):
        return obj.nombre_completo
    obtener_nombre_completo.short_description = "Nombre del Docente"
    obtener_nombre_completo.admin_order_field = 'apellido_paterno'
