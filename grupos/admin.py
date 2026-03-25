from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from .models import Grupo, GrupoAsignatura
from horarios.models import Horario
from asignaturas.models import Asignatura


class GrupoAsignaturaInline(admin.TabularInline):
    model = GrupoAsignatura
    extra = 0
    fields = ('asignatura', 'vacantes')

    def has_add_permission(self, request, obj=None):
        return obj is not None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "asignatura":
            grupo_id = request.resolver_match.kwargs.get("object_id")
            if grupo_id:
                try:
                    grupo = Grupo.objects.get(pk=grupo_id)
                    base = grupo.asignatura_base
                    equivalentes = Asignatura.objects.filter(
                        equivalencias__asignaturas=base
                    )
                    kwargs["queryset"] = (
                        Asignatura.objects.filter(pk=base.pk) | equivalentes
                    ).distinct()
                except Grupo.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class HorarioInline(admin.TabularInline):
    model = Horario
    extra = 1
    fields = ('dia', 'hora_inicio', 'hora_fin', 'tipo', 'aula', 'docente')
    autocomplete_fields = ['aula', 'docente']


@admin.action(description="Validar carga horaria")
def validar_horarios(modeladmin, request, queryset):
    correctos = 0
    for grupo in queryset:
        try:
            grupo.validar_horarios()
            correctos += 1
        except ValidationError as e:
            msg = e.message_dict if hasattr(e, 'message_dict') else e.messages
            modeladmin.message_user(
                request,
                f"Error en {grupo}: {msg}",
                level=messages.ERROR
            )
    if correctos > 0:
        modeladmin.message_user(
            request,
            f"{correctos} grupos validados correctamente.",
            level=messages.SUCCESS
        )


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'get_docentes',
        'periodo',
        'total_vacantes_display',
    )
    list_filter = ('periodo', 'asignatura_base__plan__escuela')
    search_fields = (
        'numero',
        'asignatura_base__codigo',
        'asignatura_base__nombre',
        'horarios__docente__nombres',
        'horarios__docente__apellido_paterno',
        'horarios__docente__apellido_materno',
    )
    autocomplete_fields = ['asignatura_base']
    inlines = [HorarioInline, GrupoAsignaturaInline]
    actions = [validar_horarios]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'horarios',
            'horarios__docente',
            'asignaturas_cubiertas',
            'asignaturas_cubiertas__asignatura',
        )

    @admin.display(description="Docentes")
    def get_docentes(self, obj):
        docentes = {str(h.docente) for h in obj.horarios.all() if h.docente}
        return ", ".join(docentes) if docentes else mark_safe(
            '<span style="color:red;">Sin asignar</span>'
        )

    @admin.display(description="Vacantes")
    def total_vacantes_display(self, obj):
        return obj.total_vacantes
