from django.urls import path
from . import views

urlpatterns = [
    # Listado principal de aulas
    path('', views.aula_list, name='aula_list'),

    # Formulario para registrar nueva aula
    path('nuevo/', views.aula_create, name='aula_create'),

    # Formulario para editar (recibe el ID del aula)
    path('editar/<int:pk>/', views.aula_update, name='aula_update'),

    # Confirmación y ejecución de eliminación
    path('eliminar/<int:pk>/', views.aula_delete, name='aula_delete'),
]
