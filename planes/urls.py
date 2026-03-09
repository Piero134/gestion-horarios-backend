from django.urls import path
from . import views
from . import apis
urlpatterns = [
    path('', views.planes_list, name='planes_list'),

    path('api/planes/escuela/<int:escuela_id>/', apis.api_planes_por_escuela, name='api_planes_por_escuela'),
    path('api/plan/detalle/<int:plan_id>/', apis.api_plan_detalle, name='api_plan_detalle'),

    path('importar/', views.importar_plan_estudios, name='importar_plan'),
]
