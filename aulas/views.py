from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Aula
from .forms import AulaForm
from facultades.models import Facultad

@login_required
def aula_list(request):
    # Capturar filtros de la URL
    f_facultad = request.GET.get('facultad', '')
    f_pabellon = request.GET.get('pabellon', '')
    f_tipo = request.GET.get('tipo', '')

    aulas = Aula.objects.select_related('facultad').order_by('-activo', 'pabellon', 'nombre')

    if request.user.is_superuser:
        if f_facultad:
            aulas = aulas.filter(facultad_id=f_facultad)
    else:
        # El usuario normal solo ve su facultad
        aulas = aulas.filter(facultad=request.user.facultad)

    # Filtros de Pabellón y Tipo
    if f_pabellon:
        aulas = aulas.filter(pabellon=f_pabellon)
    if f_tipo:
        aulas = aulas.filter(tipo=f_tipo)

    context = {
        'aulas': aulas,
        'pabellones': Aula.Pabellon.choices,
        'tipos': Aula.Tipo.choices,
        'facultades': Facultad.objects.all() if request.user.is_superuser else None,
        # Persistencia de filtros en el form
        'f_facultad': f_facultad,
        'f_pabellon': f_pabellon,
        'f_tipo': f_tipo,
    }
    return render(request, 'aulas/aula_list.html', context)

@login_required
def aula_create(request):
    """Crear aula validando facultad del usuario"""
    if request.method == 'POST':
        form = AulaForm(request.POST, user=request.user)
        if form.is_valid():
            aula = form.save(commit=False)
            # Si NO es superusuario, forzamos su facultad sí o sí
            if not request.user.is_superuser:
                aula.facultad = request.user.facultad
            aula.save()
            messages.success(request, "Aula creada exitosamente.")
            return redirect('aula_list')
    else:
        form = AulaForm(user=request.user)

    return render(request, 'aulas/aula_form.html', {'form': form})

@login_required
def aula_update(request, pk):
    """Editar aula validando pertenencia a la facultad"""
    # Si no es superuser, solo puede editar si el aula es de su facultad
    if request.user.is_superuser:
        aula = get_object_or_404(Aula, pk=pk)
    else:
        aula = get_object_or_404(Aula, pk=pk, facultad=request.user.facultad)

    if request.method == 'POST':
        form = AulaForm(request.POST, instance=aula, user=request.user)
        if form.is_valid():
            # Volvemos a asegurar la facultad en el save por si tocaron el HTML
            aula_editada = form.save(commit=False)
            if not request.user.is_superuser:
                aula_editada.facultad = request.user.facultad
            aula_editada.save()
            messages.success(request, "Aula actualizada correctamente.")
            return redirect('aula_list')
    else:
        form = AulaForm(instance=aula, user=request.user)

    return render(request, 'aulas/aula_form.html', {'form': form, 'object': aula})

@login_required
def aula_delete(request, pk):
    if request.user.is_superuser:
        aula = get_object_or_404(Aula, pk=pk)
    else:
        aula = get_object_or_404(Aula, pk=pk, facultad=request.user.facultad)

    if request.method == 'POST':
        aula.activo = False
        aula.save()
        messages.warning(request, f"El aula '{aula.nombre}' ha sido desactivada y ya no estará disponible para nuevos horarios.")
        return redirect('aula_list')

    return render(request, 'aulas/aula_confirm_delete.html', {'aula': aula})
