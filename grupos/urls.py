from django.urls import path
from grupos import views

urlpatterns = [
    # Lista y CRUD de grupos
    path('', views.grupos_list, name='grupos_list'),
    path('crear/', views.grupo_create, name='grupo_create'),
    path('<int:pk>/', views.grupo_detail, name='grupo_detail'),
    path('<int:pk>/editar/', views.grupo_edit, name='grupo_edit'),
    path('<int:pk>/eliminar/', views.grupo_delete, name='grupo_delete'),

    path('export-excel/', views.grupo_export_excel, name='grupo_export_excel'),
]
