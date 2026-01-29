from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Facultad

@login_required
def facultades_list(request):
    facultades = Facultad.objects.all().order_by('codigo')

    context = {
        'facultades': facultades,
        'page_title': 'Facultades',
        'page_subtitle': 'Listado de facultades registradas en el sistema'
    }

    return render(request, 'facultades_list.html', context)
