"""
API REST para la aplicación móvil Flutter.
Este módulo proporciona endpoints para intercambiar información de horarios
con la aplicación móvil.

CONEXIÓN CON APP MÓVIL FLUTTER:
- La app móvil debe hacer peticiones HTTP a estos endpoints
- Base URL: http://<servidor>:<puerto>/api/
- Todos los endpoints devuelven JSON
- Los endpoints requieren autenticación (opcional según implementación)

Endpoints disponibles:
1. GET /api/periodos/ - Lista de periodos académicos
2. GET /api/asignaturas/ - Lista de asignaturas (filtrable por plan/ciclo)
3. GET /api/grupos/ - Lista de grupos (filtrable por periodo/asignatura)
4. GET /api/grupos/<id>/ - Detalle de un grupo con sus horarios
5. GET /api/horarios/ - Lista de horarios (filtrable por grupo/dia)
6. GET /api/horarios/grupo/<grupo_id>/ - Horarios de un grupo específico
7. POST /api/horarios/conflictos/ - Detecta conflictos entre horarios
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
import json

from asignaturas.models import Asignatura
from grupos.models import Grupo
from periodos.models import PeriodoAcademico
from facultades.models import Facultad
from escuelas.models import Escuela
from .models import Horario
from .serializers import (
    serializar_periodo,
    serializar_asignatura,
    serializar_grupo,
    serializar_horario
)
from .services import detectar_conflictos_horarios


@require_http_methods(["GET"])
def api_periodos(request):
    """
    GET /api/periodos/
    Lista todos los periodos académicos.
    
    Query params:
        - activo: 'true' para filtrar solo periodos activos
    """
    periodos = PeriodoAcademico.objects.all()
    
    # Filtrar por activos si se solicita
    if request.GET.get('activo') == 'true':
        periodos = [p for p in periodos if p.activo]
        data = [serializar_periodo(p) for p in periodos]
    else:
        data = [serializar_periodo(p) for p in periodos]
    
    return JsonResponse({
        'success': True,
        'count': len(data),
        'data': data
    })


@require_http_methods(["GET"])
def api_asignaturas(request):
    """
    GET /api/asignaturas/
    Lista todas las asignaturas.
    
    Query params:
        - plan_id: Filtrar por plan de estudios
        - ciclo: Filtrar por ciclo
        - tipo: Filtrar por tipo (O, E, OP, AL)
        - search: Buscar por nombre o código
    """
    asignaturas = Asignatura.objects.select_related('plan', 'plan__escuela').all()
    
    # Filtros
    plan_id = request.GET.get('plan_id')
    if plan_id:
        asignaturas = asignaturas.filter(plan_id=plan_id)
    
    ciclo = request.GET.get('ciclo')
    if ciclo:
        asignaturas = asignaturas.filter(ciclo=ciclo)
    
    tipo = request.GET.get('tipo')
    if tipo:
        asignaturas = asignaturas.filter(tipo=tipo)
    
    search = request.GET.get('search')
    if search:
        asignaturas = asignaturas.filter(
            Q(nombre__icontains=search) | Q(codigo__icontains=search)
        )
    
    data = [serializar_asignatura(a) for a in asignaturas]
    
    return JsonResponse({
        'success': True,
        'count': len(data),
        'data': data
    })


@require_http_methods(["GET"])
def api_grupos(request):
    """
    GET /api/grupos/
    Lista todos los grupos.
    
    Query params:
        - periodo_id: Filtrar por periodo académico
        - asignatura_id: Filtrar por asignatura
        - ciclo: Filtrar por ciclo de la asignatura
        - docente_id: Filtrar por docente
        - incluir_horarios: 'true' para incluir horarios en la respuesta
    """
    grupos = Grupo.objects.select_related(
        'asignatura', 'asignatura__plan', 'periodo', 'docente'
    ).prefetch_related('horarios', 'horarios__aula').all()
    
    # Filtros
    periodo_id = request.GET.get('periodo_id')
    if periodo_id:
        grupos = grupos.filter(periodo_id=periodo_id)
    
    asignatura_id = request.GET.get('asignatura_id')
    if asignatura_id:
        grupos = grupos.filter(asignatura_id=asignatura_id)
    
    ciclo = request.GET.get('ciclo')
    if ciclo:
        grupos = grupos.filter(asignatura__ciclo=ciclo)
    
    docente_id = request.GET.get('docente_id')
    if docente_id:
        grupos = grupos.filter(docente_id=docente_id)
    
    incluir_horarios = request.GET.get('incluir_horarios') == 'true'
    
    data = [serializar_grupo(g, incluir_horarios=incluir_horarios) for g in grupos]
    
    return JsonResponse({
        'success': True,
        'count': len(data),
        'data': data
    })


@require_http_methods(["GET"])
def api_grupo_detalle(request, grupo_id):
    """
    GET /api/grupos/<id>/
    Obtiene el detalle de un grupo específico con todos sus horarios.
    """
    try:
        grupo = Grupo.objects.select_related(
            'asignatura', 'periodo', 'docente'
        ).prefetch_related('horarios', 'horarios__aula').get(id=grupo_id)
        
        data = serializar_grupo(grupo, incluir_horarios=True)
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except ObjectDoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Grupo no encontrado'
        }, status=404)


@require_http_methods(["GET"])
def api_horarios(request):
    """
    GET /api/horarios/
    Lista todos los horarios.
    
    Query params:
        - grupo_id: Filtrar por grupo
        - dia: Filtrar por día (1-7)
        - tipo: Filtrar por tipo (T, P, L)
        - periodo_id: Filtrar por periodo
    """
    horarios = Horario.objects.select_related(
        'grupo', 'grupo__asignatura', 'grupo__periodo', 'aula'
    ).all()
    
    # Filtros
    grupo_id = request.GET.get('grupo_id')
    if grupo_id:
        horarios = horarios.filter(grupo_id=grupo_id)
    
    dia = request.GET.get('dia')
    if dia:
        horarios = horarios.filter(dia=dia)
    
    tipo = request.GET.get('tipo')
    if tipo:
        horarios = horarios.filter(tipo=tipo)
    
    periodo_id = request.GET.get('periodo_id')
    if periodo_id:
        horarios = horarios.filter(grupo__periodo_id=periodo_id)
    
    data = [serializar_horario(h) for h in horarios]
    
    return JsonResponse({
        'success': True,
        'count': len(data),
        'data': data
    })


@require_http_methods(["GET"])
def api_horarios_grupo(request, grupo_id):
    """
    GET /api/horarios/grupo/<grupo_id>/
    Obtiene todos los horarios de un grupo específico organizados por día.
    
    Retorna los horarios agrupados por día de la semana.
    """
    try:
        grupo = Grupo.objects.get(id=grupo_id)
        horarios = grupo.horarios.select_related('aula').order_by('dia', 'hora_inicio')
        
        # Agrupar por día
        horarios_por_dia = {}
        for horario in horarios:
            dia_display = horario.get_dia_display()
            if dia_display not in horarios_por_dia:
                horarios_por_dia[dia_display] = []
            horarios_por_dia[dia_display].append(serializar_horario(horario))
        
        return JsonResponse({
            'success': True,
            'grupo': serializar_grupo(grupo, incluir_horarios=False),
            'horarios_por_dia': horarios_por_dia
        })
    except ObjectDoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Grupo no encontrado'
        }, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def api_detectar_conflictos(request):
    """
    POST /api/horarios/conflictos/
    Detecta conflictos entre horarios de diferentes grupos.
    
    Body JSON:
    {
        "grupos_ids": [1, 2, 3, ...],
        "periodo_id": 1  // opcional
    }
    
    Retorna:
    {
        "success": true,
        "tiene_conflictos": false,
        "conflictos": []
    }
    """
    try:
        data = json.loads(request.body)
        grupos_ids = data.get('grupos_ids', [])
        periodo_id = data.get('periodo_id')
        
        if not grupos_ids:
            return JsonResponse({
                'success': False,
                'error': 'Se requiere al menos un ID de grupo'
            }, status=400)
        
        # Usar el servicio para detectar conflictos
        resultado = detectar_conflictos_horarios(grupos_ids, periodo_id)
        
        return JsonResponse({
            'success': True,
            **resultado
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_facultades(request):
    """
    GET /api/facultades/
    Lista todas las facultades.
    """
    facultades = Facultad.objects.all()
    data = [
        {
            'id': f.id,
            'nombre': f.nombre,
            'siglas': f.siglas,
            'codigo': f.codigo
        }
        for f in facultades
    ]
    
    return JsonResponse({
        'success': True,
        'count': len(data),
        'data': data
    })


@require_http_methods(["GET"])
def api_escuelas(request):
    """
    GET /api/escuelas/
    Lista todas las escuelas profesionales.
    
    Query params:
        - facultad_id: Filtrar por facultad
    """
    escuelas = Escuela.objects.select_related('facultad').all()
    
    facultad_id = request.GET.get('facultad_id')
    if facultad_id:
        escuelas = escuelas.filter(facultad_id=facultad_id)
    
    data = [
        {
            'id': e.id,
            'nombre': e.nombre,
            'codigo': e.codigo,
            'facultad': {
                'id': e.facultad.id,
                'nombre': e.facultad.nombre
            } if e.facultad else None
        }
        for e in escuelas
    ]
    
    return JsonResponse({
        'success': True,
        'count': len(data),
        'data': data
    })
