from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Escuela, Facultad
from django.http import JsonResponse

@login_required
def escuelas_list(request, facultad_id=None):
    escuelas = Escuela.objects.select_related('facultad').all().order_by('codigo')

    facultad_filtro = None
    page_title = "Escuelas Profesionales"
    page_subtitle = "Listado general de todas las escuelas de la universidad"

    if facultad_id:
        facultad_filtro = get_object_or_404(Facultad, pk=facultad_id)
        escuelas = escuelas.filter(facultad=facultad_filtro)
        page_title = f"Escuelas de {facultad_filtro.nombre}"
        page_subtitle = f"Visualizando escuelas pertenecientes a la Facultad de {facultad_filtro.nombre}"

    context = {
        'escuelas': escuelas,
        'facultad_filtro': facultad_filtro,
        'page_title': page_title,
        'page_subtitle': page_subtitle
    }

    return render(request, 'escuelas_list.html', context)

@login_required
def api_escuelas_por_facultad(request, facultad_id):
    """API: Obtener escuelas filtradas por facultad"""
    try:
        escuelas = Escuela.objects.filter(
            facultad_id=facultad_id
        ).values('id', 'nombre', 'codigo').order_by('codigo')

        return JsonResponse({
            'success': True,
            'escuelas': list(escuelas)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def api_escuelas_fisi(request):
    """API: Obtener escuelas de la Facultad de Ingeniería de Sistemas e Informática (FISI)"""
    try:
        fisi = Facultad.objects.get(siglas='FISI')
        escuelas = Escuela.objects.filter(
            facultad=fisi
        ).values('id', 'nombre', 'codigo').order_by('codigo')

        return JsonResponse({
            'success': True,
            'escuelas': list(escuelas)
        })
    except Facultad.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Facultad de Ingeniería de Sistemas e Informática no encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
