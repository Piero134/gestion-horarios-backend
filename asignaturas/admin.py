from django.contrib import admin
from django import forms
from .models import Asignatura, Prerequisito, Ciclo

@admin.register(Ciclo)
class CicloAdmin(admin.ModelAdmin):
    search_fields = ('numero',)
    ordering = ('numero',)

class PrerequisitoInlineForm(forms.ModelForm):
    class Meta:
        model = Prerequisito
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        asignatura = getattr(self.instance, 'asignatura', None)

        if asignatura and asignatura.pk:
            self.fields['prerequisito'].queryset = Asignatura.objects.filter(
                plan=asignatura.plan,
                ciclo__numero__lt=asignatura.ciclo.numero
            ).exclude(pk=asignatura.pk)

class PrerequisitoInline(admin.TabularInline):
    model = Prerequisito
    fk_name = 'asignatura'
    extra = 0
    verbose_name = "Prerrequisito"
    verbose_name_plural = "Prerrequisitos"

    def has_add_permission(self, request, obj=None):
        # SOLO permitir agregar si la asignatura ya existe
        return obj is not None

@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ('plan', 'ciclo', 'codigo', 'nombre', 'creditos', 'tipo')
    list_filter = ('plan', 'ciclo', 'tipo')
    search_fields = ('codigo', 'nombre')
    ordering = ('plan', 'ciclo__numero', 'codigo')
    inlines = [PrerequisitoInline]
    autocomplete_fields = ('ciclo', 'plan')
