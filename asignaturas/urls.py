from django.urls import path
from . import views
from . import views_equivalencias

urlpatterns = [
    # API para filtros dinámicos
    path('api/cargar-asignaturas/', views.cargar_asignaturas_ajax, name='ajax_cargar_asignaturas'),
    path('api/asignatura-detalle/', views.obtener_equivalencias_asignatura, name='api_asignatura_equivalencias'),
    path('api/buscar-asignaturas/', views.buscar_asignaturas_ajax, name='buscar_asignaturas_ajax'),
    path('equivalencias/', views_equivalencias.lista_equivalencias, name='lista_equivalencias'),
    path('equivalencias/crear/', views_equivalencias.crear_equivalencia, name='crear_equivalencia'),
    path('equivalencias/editar/<int:pk>/', views_equivalencias.editar_equivalencia, name='editar_equivalencia'),
    path('equivalencias/eliminar/<int:pk>/', views_equivalencias.eliminar_equivalencia, name='eliminar_equivalencia'),
]
