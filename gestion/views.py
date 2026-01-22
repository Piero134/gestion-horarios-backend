from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import HorarioService

class ConsultarHorarioEstudianteView(APIView):
    def post(self, request):
        grupo_id = request.data.get('grupo')
        

        if not grupo_id:
            return Response({"error": "Faltan datos"}, status=status.HTTP_400_BAD_REQUEST)

        resultado = HorarioService.obtener_horario_estructurado(grupo_id)

        if resultado is None:
            return Response({"mensaje": "No hay horarios para este grupo/ciclo"}, status=status.HTTP_404_NOT_FOUND)

        return Response(resultado, status=status.HTTP_200_OK)