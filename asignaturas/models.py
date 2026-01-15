Aquí tienes el código completo para tu admin.py. He incluido el truco para que, al editar una Asignatura, solo puedas elegir como Prerrequisitos materias que pertenezcan al mismo Plan de Estudios, evitando así errores de mezcla entre planes.

Python

from django.contrib import admin
from django import forms
from .models import PlanEstudios, Asignatura, Prerequisito

# ==========================================
# 1. CONFIGURACIÓN PARA ASIGNATURAS
# ==========================================

class PrerequisitoInlineForm(forms.ModelForm):
    """
    Formulario personalizado para filtrar los prerrequisitos
    por el mismo plan de estudios.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'asignatura'):
            # Filtra para que solo aparezcan materias del mismo plan
            self.fields['prerequisito'].queryset = Asignatura.objects.filter(
                plan=self.instance.asignatura.plan
            ).exclude(id=self.instance.asignatura.id)

class PrerequisitoInline(admin.TabularInline):
    model = Prerequisito
    fk_name = 'asignatura'
    form = PrerequisitoInlineForm
    extra = 1
    verbose_name = "Prerrequisito"
    verbose_name_plural = "Prerrequisitos de esta asignatura"
    autocomplete_fields = ['prerequisito'] # Útil si tienes muchas materias

@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'ciclo', 'plan', 'creditos')
    list_filter = ('plan', 'ciclo')
    search_fields = ('codigo', 'nombre')
    inlines = [PrerequisitoInline]
    # Habilita búsqueda rápida para ser usado en autocompletados
    search_fields = ('codigo', 'nombre')
