from django.contrib import admin
from .models import Facultad

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
