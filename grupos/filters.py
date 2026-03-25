import django_filters
from grupos.models import Grupo, GrupoAsignatura

class GrupoFilter(django_filters.FilterSet):
    periodo = django_filters.NumberFilter(field_name='periodo')
    plan = django_filters.NumberFilter()
    ciclo = django_filters.NumberFilter()
    numero = django_filters.NumberFilter(field_name='numero')
    buscar = django_filters.CharFilter(method='filtrar_busqueda')

    class Meta:
        model = Grupo
        fields = ['periodo', 'numero']

    def __init__(self, *args, escuela=None, **kwargs):
        self.escuela = escuela
        super().__init__(*args, **kwargs)

    def filter_queryset(self, queryset):
        periodo = self.form.cleaned_data.get('periodo')
        plan_id = self.form.cleaned_data.get('plan')
        ciclo = self.form.cleaned_data.get('ciclo')
        numero = self.form.cleaned_data.get('numero')
        buscar = self.form.cleaned_data.get('buscar')

        if periodo:
            queryset = queryset.filter(periodo_id=periodo)
        if numero:
            queryset = queryset.filter(numero=numero)
        if buscar:
            queryset = queryset.buscar(buscar, escuela=self.escuela)

        # plan y ciclo anclados a la escuela
        if plan_id or ciclo:
            ga_qs = GrupoAsignatura.objects.filter(
                asignatura__plan__escuela=self.escuela
            )
            if plan_id:
                ga_qs = ga_qs.filter(asignatura__plan_id=plan_id)
            if ciclo:
                ga_qs = ga_qs.filter(asignatura__ciclo=ciclo)
            queryset = queryset.filter(asignaturas_cubiertas__in=ga_qs)

        return queryset.distinct()

    def filtrar_busqueda(self, queryset, name, value):
        return queryset
