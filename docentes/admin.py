from django.contrib import admin
from .models import Docente

@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'email')
    search_fields = ('apellido', 'nombre', 'email')
    ordering = ('apellido', 'nombre')
