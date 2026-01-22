from django.urls import path
from .views import ConsultarHorarioEstudianteView

urlpatterns = [
    path('obtener-horario/', ConsultarHorarioEstudianteView.as_view(), name='horario_estudiante'),
]