from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from escuelas.models import Escuela
from facultades.models import Facultad

from django.contrib import messages
from .forms import PlanUploadForm
from planes.models import PlanEstudios
from .utils.importer import procesar_excel_plan


@login_required
def planes_list(request):
    facultad_id = request.GET.get('facultad')
    escuela_id = request.GET.get('escuela')

    context = {
        'facultades': Facultad.objects.all(),
        'page_title': 'Planes de Estudio',
    }

    if escuela_id:
        escuela = get_object_or_404(Escuela, id=escuela_id)
        context['escuela_preseleccionada'] = escuela
        context['facultad_preseleccionada'] = escuela.facultad
    elif facultad_id:
        facultad = get_object_or_404(Facultad, id=facultad_id)
        context['facultad_preseleccionada'] = facultad

    return render(request, 'planes/planes_list.html', context)


@login_required
def importar_plan_estudios(request):
    # Bloqueo para Coordinadores de EEGG
    rol = getattr(request.user.rol, 'name', None) if hasattr(request.user, 'rol') else None
    if rol in ['Coordinador de Estudios Generales', 'Jefe de Estudios Generales']:
        messages.error(request, "Acceso denegado: Su rol no permite cargar planes.")
        return redirect('planes_list')

    if request.method == 'POST':
        form = PlanUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                # Obtenemos datos del form
                escuela = form.cleaned_data['escuela']
                anio = form.cleaned_data['anio_plan']
                archivo = request.FILES['archivo_excel']

                # Creamos el plan primero
                plan_obj, _ = PlanEstudios.objects.get_or_create(
                    anio=anio,
                    escuela=escuela
                )

                # Llamamos a la función auxiliar
                cursos, rels = procesar_excel_plan(plan_obj, archivo)

                messages.success(request, f"Procesado: {cursos} asignaturas y {rels} requisitos.")
                return redirect('planes_list')

            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    else:
        form = PlanUploadForm(user=request.user)

    return render(request, 'planes/importar_plan.html', {'form': form})
