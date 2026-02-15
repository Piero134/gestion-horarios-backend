from django.urls import path
from . import views

urlpatterns = [
    path('', views.docente_list, name='docente_list'),

    # CRUD
    path('crear/', views.docente_create, name='docente_create'),
    path('editar/<int:pk>/', views.docente_edit, name='docente_edit'),

    # Activar/Desactivar (Soft Delete)
    path('toggle-estado/<int:pk>/', views.docente_toggle_estado, name='docente_toggle_estado'),

    # API para filtros
    path('api/filtrar/', views.api_docentes_filtrar, name='api_docentes_filtrar'),

    # Legacy - redirige a toggle_estado
    path('eliminar/<int:pk>/', views.docente_delete, name='docente_delete'),
]
