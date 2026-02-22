from django.urls import path
from .views import ListadoGruposJsonView

app_name="api"

urlpatterns = [
    #path('horarios/', ListadoGruposJsonView.as_view(), name='grupos_horarios_json'),
]