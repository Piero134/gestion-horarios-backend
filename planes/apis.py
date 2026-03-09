from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

# Importa tus modelos y serializers aquí
from .models import PlanEstudios, Escuela
from .serializers import PlanDetalleSerializer, PlanSimpleSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_planes_por_escuela(request, escuela_id):
    """
    Obtiene los planes de estudio de una escuela específica.
    Ideal para llenar selectores dependientes (dropdowns).
    """
    planes = PlanEstudios.objects.filter(escuela_id=escuela_id)
    # Usamos un serializer simple para no sobrecargar la respuesta
    serializer = PlanSimpleSerializer(planes, many=True)
    return Response({
        'success': True,
        'planes': serializer.data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_plan_detalle(request, plan_id):
    """
    Retorna toda la información detallada de un solo plan.
    Incluye asignaturas y sus prerrequisitos gracias al prefetch_related.
    """
    plan = get_object_or_404(
        PlanEstudios.objects.prefetch_related('asignaturas__prerequisitos'),
        id=plan_id
    )
    serializer = PlanDetalleSerializer(plan)
    return Response(serializer.data)
