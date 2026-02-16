import django_filters
from grupos.models import Grupo

class GrupoFilter(django_filters.FilterSet):
    escuela = django_filters.NumberFilter(field_name='asignatura__plan__escuela')
    plan = django_filters.NumberFilter(field_name='asignatura__plan')
    ciclo = django_filters.NumberFilter(field_name='asignatura__ciclo')
    grupo = django_filters.NumberFilter(field_name='numero')

    buscar = django_filters.CharFilter(method='filtrar_busqueda')

    class Meta:
        model = Grupo
        fields = ['periodo', 'escuela', 'plan', 'ciclo', 'grupo']

    def filtrar_busqueda(self, queryset, name, value):
        if value:
            return queryset.buscar(value)
