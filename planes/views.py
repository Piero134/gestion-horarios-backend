from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Prefetch
from planes.models import PlanEstudios
from escuelas.models import Escuela
from facultades.models import Facultad
from asignaturas.models import Asignatura, Prerequisito

@login_required
def planes_list(request):
    facultad_id = request.GET.get('facultad')
    escuela_id = request.GET.get('escuela')
    plan_id = request.GET.get('plan')

    # Contexto inicial
    context = {
        'page_title': 'Planes de Estudio',
        'page_subtitle': 'Gestión y visualización de planes curriculares',
        'facultades': Facultad.objects.all().order_by('codigo'),
    }

    if escuela_id:
        escuela = get_object_or_404(Escuela, id=escuela_id)
        context['escuela_preseleccionada'] = escuela
        context['facultad_preseleccionada'] = escuela.facultad
        context['page_title'] = f'Planes de Estudio - {escuela.nombre}'

    if plan_id:
        plan = get_object_or_404(
            PlanEstudios.objects.select_related('escuela__facultad'),
            id=plan_id
        )
        context['plan_seleccionado'] = plan

    return render(request, 'planes_list.html', context)

@login_required
def api_planes_por_escuela(request, escuela_id):
    """API: Obtener planes de estudio filtrados por escuela"""
    try:
        planes = PlanEstudios.objects.filter(
            escuela_id=escuela_id
        ).annotate(
            total_asignaturas=Count('asignaturas'),
            total_creditos=Count('asignaturas__creditos')
        ).values(
            'id', 'nombre', 'total_asignaturas', 'total_creditos'
        ).order_by('-nombre')

        return JsonResponse({
            'success': True,
            'planes': list(planes)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def api_plan_detalle(request, plan_id):
    """API: Obtener detalle completo de un plan de estudios con sus asignaturas"""
    try:
        plan = get_object_or_404(
            PlanEstudios.objects.select_related('escuela__facultad')
            .prefetch_related(
                Prefetch(
                    'asignaturas',
                    queryset=Asignatura.objects.prefetch_related(
                        'prerequisitos'
                    ).order_by('ciclo', 'codigo')
                )
            ),
            id=plan_id
        )

        # Organizar asignaturas por ciclo
        asignaturas_por_ciclo = {}
        total_creditos = 0

        for asignatura in plan.asignaturas.all():
            ciclo = asignatura.ciclo

            if ciclo not in asignaturas_por_ciclo:
                asignaturas_por_ciclo[ciclo] = {
                    'ciclo': ciclo,
                    'asignaturas': [],
                    'creditos_ciclo': 0
                }

            # Obtener prerequisitos
            prerequisitos = []
            for prereq in asignatura.prerequisitos.all():
                prerequisitos.append({
                    'id': prereq.id,
                    'codigo': prereq.codigo,
                    'nombre': prereq.nombre,
                    'ciclo': prereq.ciclo
                })

            asignatura_data = {
                'id': asignatura.id,
                'codigo': asignatura.codigo,
                'nombre': asignatura.nombre,
                'tipo': asignatura.tipo,
                'tipo_display': asignatura.get_tipo_display(),
                'creditos': asignatura.creditos,
                'horas_teoria': asignatura.horas_teoria,
                'horas_practica': asignatura.horas_practica,
                'horas_laboratorio': asignatura.horas_laboratorio,
                'prerequisitos': prerequisitos
            }

            asignaturas_por_ciclo[ciclo]['asignaturas'].append(asignatura_data)
            asignaturas_por_ciclo[ciclo]['creditos_ciclo'] += asignatura.creditos
            total_creditos += asignatura.creditos

        # Convertir a lista ordenada
        ciclos_data = sorted(asignaturas_por_ciclo.values(), key=lambda x: x['ciclo'])

        return JsonResponse({
            'success': True,
            'plan': {
                'id': plan.id,
                'nombre': plan.nombre,
                'escuela': {
                    'id': plan.escuela.id,
                    'nombre': plan.escuela.nombre,
                    'codigo': plan.escuela.codigo
                },
                'facultad': {
                    'id': plan.escuela.facultad.id,
                    'nombre': plan.escuela.facultad.nombre,
                    'siglas': plan.escuela.facultad.siglas
                },
                'total_asignaturas': plan.asignaturas.count(),
                'total_creditos': total_creditos,
                'total_ciclos': len(ciclos_data),
                'ciclos': ciclos_data
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def api_buscar_planes(request):
    """API: Búsqueda de planes con filtros múltiples"""
    try:
        query = request.GET.get('q', '')
        facultad_id = request.GET.get('facultad')
        escuela_id = request.GET.get('escuela')

        planes = PlanEstudios.objects.select_related('escuela__facultad')

        # Aplicar filtros
        if query:
            planes = planes.filter(
                Q(nombre__icontains=query) |
                Q(escuela__nombre__icontains=query)
            )

        if facultad_id:
            planes = planes.filter(escuela__facultad_id=facultad_id)

        if escuela_id:
            planes = planes.filter(escuela_id=escuela_id)

        # Anotar con estadísticas
        planes = planes.annotate(
            total_asignaturas=Count('asignaturas')
        )

        # Serializar resultados
        resultados = []
        for plan in planes[:50]:  # Limitar a 50 resultados
            resultados.append({
                'id': plan.id,
                'nombre': plan.nombre,
                'escuela': plan.escuela.nombre,
                'escuela_codigo': plan.escuela.codigo,
                'facultad': plan.escuela.facultad.siglas,
                'total_asignaturas': plan.total_asignaturas
            })

        return JsonResponse({
            'success': True,
            'count': len(resultados),
            'planes': resultados
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
