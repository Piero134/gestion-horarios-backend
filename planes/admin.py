from django.contrib import admin
from asignaturas.models import Asignatura, Prerequisito
from .models import PlanEstudios

class AsignaturaEnPlanInline(admin.TabularInline):
    model = Asignatura
    extra = 0
    fields = ('codigo', 'nombre', 'ciclo', 'creditos')
    readonly_fields = ('codigo', 'nombre', 'ciclo', 'creditos')
    show_change_link = True # Permite ir a la asignatura
    can_delete = False
    verbose_name = "Asignatura del Plan"
    verbose_name_plural = "Malla Curricular (Vista Rápida)"

@admin.register(PlanEstudios)
class PlanEstudiosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'escuela')
    list_filter = ('escuela',)
    search_fields = ('nombre', 'escuela__nombre')
    inlines = [AsignaturaEnPlanInline]

@admin.register(Prerequisito)
class PrerequisitoAdmin(admin.ModelAdmin):
    list_display = ('prerequisito', 'asignatura')
    search_fields = ('asignatura__codigo', 'prerequisito__codigo')
