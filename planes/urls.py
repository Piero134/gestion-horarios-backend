from django.urls import path
from . import views

urlpatterns = [
    path('', views.planes_list, name='planes_list'),

    path('api/planes/escuela/<int:escuela_id>/', views.api_planes_por_escuela, name='api_planes_por_escuela'),
    path('api/plan/<int:plan_id>/detalle/', views.api_plan_detalle, name='api_plan_detalle'),
    path('api/planes/buscar/', views.api_buscar_planes, name='api_buscar_planes'),
]
