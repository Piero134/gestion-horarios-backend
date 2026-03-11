from django.urls import path
from .views import *

app_name='horarios'

urlpatterns = [
    # API REST para app móvil
    path('api/horarios/', HorarioPorDiaListView.as_view(), name='api_horarios'),

    # Vistas para la interfaz web
    path('', horario_asignaturas, name='horario_asignaturas'),
    
    path('api/v1/horarios/check-update/', VerificacionActualizacionHorarioView.as_view(), name='api-horarios-check-update')
]
