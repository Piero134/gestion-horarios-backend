from django.urls import path
from . import views

urlpatterns = [
    # API para filtros dinámicos
    path('api/cargar-asignaturas/', views.cargar_asignaturas_ajax, name='ajax_cargar_asignaturas'),
    path('api/asignatura-detalle/', views.obtener_equivalencias_asignatura, name='api_asignatura_equivalencias'),
]
