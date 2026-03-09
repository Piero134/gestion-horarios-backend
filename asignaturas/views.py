from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from asignaturas.models import Asignatura

@login_required
def cargar_asignaturas_ajax(request):
    escuela_id = request.GET.get('escuela_id')
    ciclo = request.GET.get('ciclo')

    if not escuela_id:
        return JsonResponse([], safe=False)

    asignaturas = Asignatura.objects.filter(
        plan__escuela_id=escuela_id
    ).select_related('plan').order_by('ciclo', 'codigo')

    if ciclo:
        asignaturas = asignaturas.filter(ciclo=ciclo)

    # Formato compatible con Select2 y tu HTML
    data = []
    for asig in asignaturas:
        data.append({
            'id': asig.id,
            'text': f"{asig.codigo} - {asig.nombre}",
            'ciclo': asig.ciclo
        })

    return JsonResponse(data, safe=False)

@login_required
def obtener_equivalencias_asignatura(request):
    asignatura_id = request.GET.get('id')
    if not asignatura_id:
        return JsonResponse({'error': 'No ID provided'}, status=400)

    try:
        asignatura = Asignatura.objects.select_related('plan', 'plan__escuela').get(pk=asignatura_id)

        equivalencias_qs = Asignatura.objects.filter(
            equivalencias__asignaturas=asignatura
        ).exclude(
            id=asignatura.id
        ).select_related(
            'plan',
            'plan__escuela'
        ).distinct()

        user = request.user
        if hasattr(user, 'rol') and user.rol.name == 'Vicedecano Académico':
            equivalencias_qs = equivalencias_qs.filter(
                plan__escuela__facultad=user.facultad
            )
        elif hasattr(user, 'escuela') and user.escuela:
            equivalencias_qs = equivalencias_qs.filter(
                plan__escuela=user.escuela
            )

        equivalentes = []
        for asig in equivalencias_qs:
            equivalentes.append({
                'id': asig.id,
                'codigo': asig.codigo,
                'nombre': asig.nombre,
                'plan': f"Plan {asignatura.plan.anio}",
                'escuela': asig.plan.escuela.nombre,
                'text': f"[{asig.plan.escuela.nombre}] {asig.nombre}"
            })

        data = {
            'id': asignatura.id,
            'principal': {
                'codigo': asignatura.codigo,
                'nombre': asignatura.nombre,
                'plan': f"Plan {asignatura.plan.anio}",
                'escuela': asignatura.plan.escuela.nombre
            },
            'equivalencias': equivalentes,

            'horas_teoria': asignatura.horas_teoria,
            'horas_practica': asignatura.horas_practica,
            'horas_laboratorio': asignatura.horas_laboratorio
        }

        return JsonResponse(data)

    except Asignatura.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
