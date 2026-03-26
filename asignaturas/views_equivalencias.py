from django.contrib.auth.decorators import login_required

from asignaturas.models import Equivalencia
from escuelas.models import Escuela
from django.shortcuts import render, redirect
from django.contrib import messages

from django.shortcuts import get_object_or_404
import json

@login_required
def crear_equivalencia(request):
    facultad = getattr(request.user, 'facultad', None)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        asignaturas_ids = request.POST.getlist('asignaturas')

        if nombre and asignaturas_ids:
            equivalencia = Equivalencia.objects.create(nombre=nombre)
            equivalencia.asignaturas.set(asignaturas_ids)
            messages.success(request, 'Equivalencia registrada correctamente.')
            return redirect('lista_equivalencias')
        else:
            messages.error(request, 'Debe ingresar un nombre y al menos una asignatura.')

    escuelas = Escuela.objects.filter(facultad=facultad) if facultad else Escuela.objects.all()

    return render(request, 'equivalencias/form_equivalencia.html', {
        'facultad': facultad,
        'escuelas': escuelas,
    })

@login_required
def editar_equivalencia(request, pk):
    equivalencia = get_object_or_404(Equivalencia, pk=pk)
    facultad = getattr(request.user, 'facultad', None)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        asignaturas_ids = request.POST.getlist('asignaturas')

        if nombre and asignaturas_ids:
            equivalencia.nombre = nombre
            equivalencia.save()
            # .set() reemplaza las asignaturas anteriores por las nuevas seleccionadas
            equivalencia.asignaturas.set(asignaturas_ids)
            messages.success(request, 'Equivalencia actualizada correctamente.')
            return redirect('lista_equivalencias')
        else:
            messages.error(request, 'Debe ingresar un nombre y al menos una asignatura.')

    escuelas = Escuela.objects.filter(facultad=facultad) if facultad else Escuela.objects.all()

    asignaturas_precargadas = []
    for asig in equivalencia.asignaturas.select_related('plan__escuela'):
        asignaturas_precargadas.append({
            'id': str(asig.id),
            'text': f"[{asig.codigo}] {asig.nombre}",
            'nombre_limpio': asig.nombre,
            'escuela_nombre': asig.plan.escuela.nombre,
            'plan_anio': asig.plan.anio,
            'ciclo': asig.ciclo
        })

    return render(request, 'equivalencias/form_equivalencia.html', {
        'equivalencia': equivalencia,
        'escuelas': escuelas,
        # Convertimos la lista a JSON para que JS pueda iterarla
        'asignaturas_precargadas_json': json.dumps(asignaturas_precargadas),
        'accion': 'Editar',
    })

@login_required
def eliminar_equivalencia(request, pk):
    if request.method == 'POST':
        equivalencia = get_object_or_404(Equivalencia, pk=pk)
        equivalencia.delete()
        messages.success(request, 'Equivalencia eliminada correctamente.')
    return redirect('lista_equivalencias')

@login_required
def lista_equivalencias(request):
    facultad = getattr(request.user, 'facultad', None)

    queryset = Equivalencia.objects.prefetch_related(
        'asignaturas__plan__escuela'
    )

    if facultad:
        queryset = queryset.filter(
            asignaturas__plan__escuela__facultad=facultad
        ).distinct()

    return render(request, 'equivalencias/lista_equivalencias.html', {
        'equivalencias': queryset
    })
