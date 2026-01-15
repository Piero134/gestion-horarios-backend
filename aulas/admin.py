from django.contrib import admin
from .models import Aula

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'tipo', 'capacidad', 'ubicacion')
    list_filter = ('tipo', 'ubicacion')
    search_fields = ('codigo', 'ubicacion')
    ordering = ('codigo',)
