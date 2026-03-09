from django.contrib import admin
from django import forms
from .models import Asignatura, Equivalencia, Prerequisito

class PrerequisitoInlineForm(forms.ModelForm):
    class Meta:
        model = Prerequisito
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        asignatura = getattr(self.instance, 'asignatura', None)

        if asignatura and asignatura.pk:
            self.fields['prerequisito'].queryset = (
                Asignatura.objects
                .filter(
                    plan=asignatura.plan,
                    ciclo__lt=asignatura.ciclo
                )
                .exclude(pk=asignatura.pk)
            )

class PrerequisitoInline(admin.TabularInline):
    model = Prerequisito
    form = PrerequisitoInlineForm
    fk_name = 'asignatura'
    extra = 0
    verbose_name = "Prerrequisito"
    verbose_name_plural = "Prerrequisitos"

    def has_add_permission(self, request, obj=None):
        # SOLO permitir agregar si la asignatura ya existe
        return obj is not None

@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'plan', 'ciclo',  'creditos', 'tipo')
    list_filter = ('plan__escuela', 'ciclo', 'tipo')
    search_fields = ('codigo', 'nombre')
    ordering = ('plan', 'ciclo', 'codigo')
    inlines = [PrerequisitoInline]

    autocomplete_fields = ('plan',)

@admin.register(Equivalencia)
class EquivalenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'asignaturas_count')
    search_fields = ('nombre', 'asignaturas__codigo', 'asignaturas__nombre')

    filter_horizontal = ('asignaturas',)
    def asignaturas_count(self, obj):
        return obj.asignaturas.count()
    asignaturas_count.short_description = "Asignaturas equivalentes"
