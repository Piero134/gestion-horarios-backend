from django.contrib import admin
from .models import PlanEstudios

@admin.register(PlanEstudios)
class PlanEstudiosAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'escuela')
    list_filter = ('escuela',)
    search_fields = ('nombre',)
