from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as views

urlpatterns = [
    path('', views.escuelas_list, name='escuelas_list'),

    path('api/escuelas/<int:facultad_id>/', views.api_escuelas_por_facultad, name='api_escuelas_por_facultad'),
]
