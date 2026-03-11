from django.urls import path
from . import views as views

urlpatterns = [
    path('', views.escuelas_list, name='escuelas_list'),

    path('api/escuelas/<int:facultad_id>/', views.api_escuelas_por_facultad, name='api_escuelas_por_facultad'),

    path('api/escuelas/fisi/', views.api_escuelas_fisi, name='api_escuelas_fisi'),
]
