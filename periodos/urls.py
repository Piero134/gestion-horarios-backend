from django.urls import path
from . import views

urlpatterns = [
    path('', views.periodo_list, name='periodo_list'),
    path('sincronizar/', views.sincronizar_periodos_view, name='periodo_sync'),
]
