from django.urls import path, include
from grupos import views
from rest_framework.routers import DefaultRouter
from .api import GrupoViewSet
router = DefaultRouter()

router.register(r'grupos', GrupoViewSet, basename='grupo')

urlpatterns = [
    # Lista y CRUD de grupos
    path('', views.grupos_list, name='grupos_list'),
    path('crear/', views.grupo_create, name='grupo_create'),
    path('<int:pk>/', views.grupo_detail, name='grupo_detail'),
    path('<int:pk>/editar/', views.grupo_edit, name='grupo_edit'),
    path('<int:pk>/eliminar/', views.grupo_delete, name='grupo_delete'),

    path('importar/', views.importar_grupos_view, name='importar_grupos'),
    path('api/', include(router.urls)),
]
