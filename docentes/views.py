from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Docente
from .forms import DocenteForm
from facultades.models import Facultad
from django.http import JsonResponse

@login_required
def api_docentes_filtrar(request):
    facultad_id = request.GET.get('facultad_id')
    departamento_id = request.GET.get('departamento_id')
    tipo = request.GET.get('tipo', '').strip()
    estado = request.GET.get('estado', 'activos')
    busqueda = request.GET.get('q', '').strip()

    # REGLA DE NEGOCIO: Facultad es estrictamente necesaria
    if not facultad_id:
        return JsonResponse({'docentes': []}) # Retorna lista vacía si no hay facultad

    queryset = Docente.objects.select_related(
        'departamento',
        'departamento__facultad',
        'facultad'
    ).all()

    # Filtro por Facultad (obligatorio)
    queryset = queryset.filter(facultad_id=facultad_id)

    if estado == 'activos':
        queryset = queryset.filter(activo=True)
    elif estado == 'inactivos':
        queryset = queryset.filter(activo=False)

    # Fitlro por tipo
    if tipo in ['N', 'C']:
        queryset = queryset.filter(tipo=tipo)

    # Filtro por Departamento
    if departamento_id:
        queryset = queryset.filter(departamento_id=departamento_id)

    # 2. Buscador de Texto (opcional)
    if busqueda:
        queryset = queryset.filter(
            Q(nombres__icontains=busqueda) |
            Q(apellido_paterno__icontains=busqueda) |
            Q(apellido_materno__icontains=busqueda) |
            Q(dni__icontains=busqueda) |
            Q(codigo__icontains=busqueda)
        )

    # 3. Serialización
    data = []
    for d in queryset:
        item = {
            'id': d.id,
            'nombre_completo': d.nombre_completo,
            'email': d.email or "",
            'tipo': d.tipo,
            'dni': d.dni,
            'codigo': d.codigo or "",
            'departamento': d.departamento.nombre if d.departamento else "-",
            'departamento_id': d.departamento.id if d.departamento else None,
            'categoria': d.get_categoria_display() if d.categoria else "",
            'dedicacion': d.get_dedicacion_display() if d.dedicacion else "",
            'activo': d.activo,
            'url_editar': f"/docentes/editar/{d.id}/",
            'url_toggle_estado': f"/docentes/toggle-estado/{d.id}/",
        }
        data.append(item)

    return JsonResponse({'docentes': data})

@login_required
def docente_list(request):
    # Solo enviamos las Facultades. Los departamentos se cargarán por AJAX.
    facultades = Facultad.objects.all()

    context = {
        'facultades': facultades,
        'titulo': 'Gestión de Docentes'
    }
    return render(request, 'docentes/docente_list.html', context)

@login_required
def docente_create(request):
    if request.method == 'POST':
        form = DocenteForm(request.POST)
        if form.is_valid():
            docente = form.save()
            messages.success(request, f"Docente {docente.nombre_completo} registrado exitosamente.")
            return redirect('docente_list')
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = DocenteForm()

    context = {
        'form': form,
        'action': 'Registrar'
    }
    return render(request, 'docentes/docente_form.html', context)

@login_required
def docente_edit(request, pk):
    docente = get_object_or_404(Docente, pk=pk)

    if request.method == 'POST':
        form = DocenteForm(request.POST, instance=docente)
        if form.is_valid():
            form.save()
            messages.success(request, f"Datos del docente {docente.nombre_completo} actualizados.")
            return redirect('docente_list')
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = DocenteForm(instance=docente)

    context = {
        'form': form,
        'action': 'Editar'
    }
    return render(request, 'docentes/docente_form.html', context)

@login_required
def docente_toggle_estado(request, pk):
    """
    Activa o desactiva un docente (soft delete).
    """
    docente = get_object_or_404(Docente, pk=pk)

    if request.method == 'POST':
        if docente.activo:
            docente.desactivar()
            messages.success(request, f"Docente {docente.nombre_completo} desactivado correctamente.")
        else:
            docente.activar()
            messages.success(request, f"Docente {docente.nombre_completo} reactivado correctamente.")

        return redirect('docente_list')

    context = {
        'docente': docente,
        'accion': 'desactivar' if docente.activo else 'reactivar'
    }
    return render(request, 'docentes/docente_toggle_estado.html', context)

@login_required
def docente_delete(request, pk):
    """
    Vista legacy - ahora redirige a toggle_estado.
    Mantenida por compatibilidad.
    """
    return redirect('docente_toggle_estado', pk=pk)
