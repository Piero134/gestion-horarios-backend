from django.contrib import admin
from django import forms
from .models import Asignatura, Prerequisito

class PrerequisitoInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and hasattr(self.instance, 'asignatura') and self.instance.asignatura_id:
            asignatura_actual = self.instance.asignatura

            self.fields['prerequisito'].queryset = Asignatura.objects.filter(
                plan=asignatura_actual.plan,
                ciclo__lt=asignatura_actual.ciclo
            ).exclude(id=asignatura_actual.id)

        elif 'initial' in kwargs and 'asignatura' in kwargs['initial']:
            # Caso inicial
            pass

class PrerequisitoInline(admin.TabularInline):
    model = Prerequisito
    fk_name = 'asignatura'
    form = PrerequisitoInlineForm
    extra = 1
    verbose_name = "Prerrequisito"
    verbose_name_plural = "Prerrequisitos de esta asignatura"
    autocomplete_fields = ['prerequisito']

@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'ciclo', 'plan', 'creditos')
    list_filter = ('plan', 'ciclo')
    search_fields = ('codigo', 'nombre')
    inlines = [PrerequisitoInline]
    search_fields = ('codigo', 'nombre')
