from django.urls import path
from .views import *

app_name='horarios'

urlpatterns = [
    # API REST para app móvil
    path('api/horarios/', HorarioPorDiaListView.as_view(), name='api_horarios'),

]
