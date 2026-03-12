from django.shortcuts import render
from periodos.models import PeriodoAcademico
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    # Periodo activo o mas reciente
    context = {
        'page_title': 'Inicio | SGH-FISI',
        'semestre_actual': PeriodoAcademico.objects.get_activo() or PeriodoAcademico.objects.order_by('-anio', '-nombre').first(),
        'usuario_nombre': request.user.first_name or request.user.username,
    }

    return render(request, 'home.html', context)
