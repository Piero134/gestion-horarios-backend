import django_filters
from horarios.models import Horario

class HorarioFilter(django_filters.FilterSet):
    periodo = django_filters.NumberFilter(field_name='grupo__periodo')
    grupo = django_filters.NumberFilter(field_name='grupo__numero')

    class Meta:
        model = Horario
        fields = ['periodo', 'grupo']
