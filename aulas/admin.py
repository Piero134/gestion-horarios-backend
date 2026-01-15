from django.contrib import admin
from .models import Aula

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'tipo', 'capacidad')
    search_fields = ('codigo',)
    ordering = ('codigo',)
