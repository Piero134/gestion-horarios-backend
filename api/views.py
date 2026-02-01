from rest_framework import generics
from rest_framework.permissions import AllowAny # Para que puedas probar sin login
from grupos.models import Grupo
from .serializers import GrupoCustomSerializer

class ListadoGruposJsonView(generics.ListAPIView):
    serializer_class = GrupoCustomSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):

        return Grupo.objects.all().prefetch_related(
            'horarios',           
            'horarios__aula',      
            'asignatura',         
            'docente',
        )            