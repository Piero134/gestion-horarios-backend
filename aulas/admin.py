from django.contrib import admin
from .models import Aula

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad', 'es_laboratorio')
    list_filter = ('es_laboratorio',)
    search_fields = ('nombre',)
    ordering = ('nombre',)
