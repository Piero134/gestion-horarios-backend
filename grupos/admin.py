from django.contrib import admin
from .models import Grupo, DistribucionVacantes
from horarios.models import Horario
from asignaturas.models import Asignatura
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

class DistribucionVacantesInline(admin.TabularInline):
    model = DistribucionVacantes
    extra = 0
    fields = ('asignatura', 'cantidad', 'matriculados')
    readonly_fields = ('matriculados',)

    def has_add_permission(self, request, obj=None):
        return obj is not None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "asignatura":
            grupo_id = request.resolver_match.kwargs.get("object_id")
            if grupo_id:
                try:
                    grupo = Grupo.objects.get(pk=grupo_id)
                    base = grupo.asignatura
                    # Lógica para filtrar asignaturas equivalentes
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
            # Extraemos el mensaje de error
            msg = e.message_dict if hasattr(e, 'message_dict') else e.messages
            modeladmin.message_user(request, f"Error en {grupo}: {msg}", level=messages.ERROR)

    if correctos > 0:
        modeladmin.message_user(request, f"{correctos} grupos validados.", level=messages.SUCCESS)

@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'get_docentes',
        'periodo',
        'total_vacantes_display'
    )

    list_filter = ('periodo', 'asignatura__plan__escuela')

    # Búsqueda optimizada (incluyendo búsqueda inversa a docentes)
    search_fields = (
        'numero',
        'asignatura__codigo',
        'asignatura__nombre',
        'horarios__docente__nombre',
        'horarios__docente__apellido'
    )

    autocomplete_fields = ['asignatura']
    inlines = [HorarioInline, DistribucionVacantesInline]
    actions = [validar_horarios]

    def get_queryset(self, request):
        # Optimización para evitar N+1 queries
        return super().get_queryset(request).prefetch_related('horarios', 'horarios__docente')

    @admin.display(description="Docentes")
    def get_docentes(self, obj):
        docentes = {f"{h.docente}" for h in obj.horarios.all() if h.docente}
        return ", ".join(docentes) if docentes else mark_safe('<span style="color:red;">Sin asignar</span>')

    @admin.display(description="Vacantes")
    def total_vacantes_display(self, obj):
        return obj.total_vacantes
