from django.contrib import admin
from .models import Grupo, DistribucionVacantes
from horarios.models import Horario
from django import forms
from asignaturas.models import Asignatura
from django.contrib import admin, messages
from django.core.exceptions import ValidationError

class DistribucionVacantesInline(admin.TabularInline):
    model = DistribucionVacantes
    extra = 0
    fields = ('asignatura', 'cantidad', 'matriculados')
    readonly_fields = ('matriculados',)

    def has_add_permission(self, request, obj=None):
        # No permitir agregar si el grupo aún no existe
        return obj is not None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "asignatura":
            grupo_id = request.resolver_match.kwargs.get("object_id")

            if grupo_id:
                grupo = Grupo.objects.get(pk=grupo_id)
                base = grupo.asignatura

                equivalentes = Asignatura.objects.filter(
                    equivalencias__asignaturas=base
                )

                kwargs["queryset"] = (
                    Asignatura.objects.filter(pk=base.pk) | equivalentes
                ).distinct()

            else:
                kwargs["queryset"] = Asignatura.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class HorarioInline(admin.TabularInline):
    model = Horario
    extra = 1
    autocomplete_fields = ['aula']

@admin.action(description="Validar carga horaria del grupo")
def validar_horarios(modeladmin, request, queryset):
    for grupo in queryset:
        try:
            grupo.validar_horarios()
            messages.success(
                request,
                f"{grupo}: carga horaria CORRECTA ✅"
            )
        except ValidationError as e:
            messages.error(
                request,
                f"{grupo}: {e.messages[0]}"
            )

@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'asignatura',
        'docente',
        'periodo',
        'total_vacantes'
    )

    readonly_fields = ('total_vacantes',)

    actions = [validar_horarios]

    list_filter = (
        'periodo',
        'asignatura__plan__escuela'
    )

    search_fields = (
        'numero',
        'asignatura__codigo',
        'asignatura__nombre',
        'docente__nombre'
    )

    autocomplete_fields = ['asignatura', 'docente']

    inlines = [
        HorarioInline,
        DistribucionVacantesInline
    ]

    def total_vacantes(self, obj):
        return obj.total_vacantes

    total_vacantes.short_description = "Vacantes Totales"
