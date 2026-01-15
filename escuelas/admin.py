from django.contrib import admin
from .models import Escuela

@admin.register(Escuela)
class EscuelaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
