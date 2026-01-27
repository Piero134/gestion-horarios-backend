from django.contrib import admin
from .models import Escuela

@admin.register(Escuela)
class EscuelaAdmin(admin.ModelAdmin):
    list_display = ('facultad', 'codigo', 'nombre')

    list_filter = ('facultad',)

    search_fields = ('nombre', 'codigo',)

    ordering = ('facultad__codigo', 'codigo',)

    readonly_fields = ('codigo',)
