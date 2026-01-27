from django.contrib import admin
from asignaturas.models import Asignatura, Prerequisito
from .models import PlanEstudios

class AsignaturaEnPlanInline(admin.TabularInline):
    model = Asignatura
    extra = 0
    fields = ('codigo', 'nombre', 'ciclo', 'creditos', 'prerrequisitos_str')
    readonly_fields = fields
    ordering = ('ciclo', 'codigo')
    show_change_link = True # Permite ir a la asignatura
    can_delete = False
    verbose_name = "Asignatura del Plan"
    verbose_name_plural = "Malla Curricular"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('prerequisitos')

    def prerrequisitos_str(self, obj):
        prereqs = obj.prerequisitos.all()
        if not prereqs:
            return "—"
        return "\n".join(str(p) for p in prereqs)

    prerrequisitos_str.short_description = "Prerrequisitos"

@admin.register(PlanEstudios)
class PlanEstudiosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'escuela')
    list_filter = ('escuela',)
    search_fields = ('nombre', 'escuela__nombre')
    inlines = [AsignaturaEnPlanInline]
    ordering = ('escuela__codigo', 'nombre')

@admin.register(Prerequisito)
class PrerequisitoAdmin(admin.ModelAdmin):
    list_display = ('prerequisito', 'asignatura')
    search_fields = ('asignatura__codigo', 'prerequisito__codigo')
