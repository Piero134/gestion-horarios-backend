from django.urls import path
from .views import *

app_name='horarios'

urlpatterns = [
    # API REST para app móvil
    # path('api/periodos/', views.api_periodos, name='api_periodos'),
    # path('api/asignaturas/', views.api_asignaturas, name='api_asignaturas'),
    # path('api/grupos/', views.api_grupos, name='api_grupos'),
    # path('api/grupos/<int:grupo_id>/', views.api_grupo_detalle, name='api_grupo_detalle'),
    path('api/horarios/', api_horarios.as_view(), name='api_horarios'),
    # path('api/horarios/grupo/<int:grupo_id>/', views.api_horarios_grupo, name='api_horarios_grupo'),
    # path('api/horarios/conflictos/', views.api_detectar_conflictos, name='api_conflictos'),
    # path('api/facultades/', views.api_facultades, name='api_facultades'),
    # path('api/escuelas/', views.api_escuelas, name='api_escuelas'),
]
