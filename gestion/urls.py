from django.urls import path
from .views import ConsultarHorarioEstudianteView

urlpatterns = [
    # Esta es la ruta que llamará tu "promesa" desde el frontend
    path('obtener-horario/', ConsultarHorarioEstudianteView.as_view(), name='horario_estudiante'),
]