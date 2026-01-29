from django.urls import path
from django.contrib.auth import views as auth_views
from .views import facultades_list
from escuelas import views

urlpatterns = [
    path('', facultades_list, name='facultades_list'),
    path('<int:facultad_id>/escuelas/', views.escuelas_list, name='escuelas_por_facultad'),
]
