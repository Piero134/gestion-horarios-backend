from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Facultad, Departamento
from django.http import JsonResponse

@login_required
def facultades_list(request):
    facultades = Facultad.objects.all().order_by('codigo')

    context = {
        'facultades': facultades,
        'page_title': 'Facultades',
        'page_subtitle': 'Listado de facultades registradas en el sistema'
    }

    return render(request, 'facultades_list.html', context)

@login_required
def api_load_departamentos(request):
    facultad_id = request.GET.get('facultad_id')
    if not facultad_id:
        return JsonResponse({'departamentos': []})

    # Filtramos departamentos que pertenecen a esa facultad
    departamentos = Departamento.objects.filter(facultad_id=facultad_id).order_by('nombre')

    data = [{'id': d.id, 'nombre': d.nombre} for d in departamentos]
    return JsonResponse({'departamentos': data})
