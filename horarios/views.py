from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny # Para que puedas probar sin login
from grupos.models import Grupo
from .serializers import GrupoCustomSerializer

class api_horarios(generics.ListAPIView):
    serializer_class = GrupoCustomSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # 1. Consulta base con prefetch_related para optimizar la base de datos
        queryset = Grupo.objects.all().prefetch_related(
            'horarios',          
            'horarios__aula',      
            'asignatura',        
            'docente',
        )            

        # 2. Capturamos los filtros desde la URL (ej: ?grupo_id=1 o ?periodo_id=2)
        grupo_id = self.request.query_params.get('grupo_id', None)
        numero_grupo = self.request.query_params.get('numero', None)
        periodo_id = self.request.query_params.get('periodo_id', None)

        # 3. Aplicamos los filtros solo si el móvil los envía
        if grupo_id is not None:
            queryset = queryset.filter(id=grupo_id)
            
        if numero_grupo is not None:
            queryset = queryset.filter(numero=numero_grupo)

        if periodo_id is not None:
            queryset = queryset.filter(periodo_id=periodo_id)

        # Retorna los datos filtrados (o todos si no se mandó ningún filtro)
        return queryset