from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from grupos.models import Grupo, GrupoAsignatura
from grupos.forms import (
    GrupoForm,
    HorarioFormSet,
    GrupoAsignaturaFormSet,
)
from periodos.models import PeriodoAcademico
from escuelas.models import Escuela
from planes.models import PlanEstudios
from .filters import GrupoFilter
from .utils.importer import importar_programacion, ExcelImportError
from .excel_forms import UploadExcelForm
from django.db.models import OuterRef, Subquery

def _get_periodo_activo_o_redirigir(request):
    """Devuelve el periodo activo o None si no existe (ya emite el mensaje de error)."""
    periodo = PeriodoAcademico.objects.get_activo()
    if not periodo:
        messages.error(
            request,
            'No existe un periodo académico activo. Contacte al administrador.'
        )
    return periodo

@login_required
def grupos_list(request):
    user = request.user

    escuelas = Escuela.objects.para_usuario(user).order_by('codigo')
    if not escuelas.exists():
        return render(request, 'grupos/grupos_list.html', {'grupos': []})

    escuela_id = request.GET.get('escuela')
    if not (escuela_id and str(escuela_id).isdigit() and escuelas.filter(id=escuela_id).exists()):
        escuela_id = str(escuelas.first().id)

    escuela = escuelas.get(id=escuela_id)

    rol_name = getattr(user.rol, 'name', None) if hasattr(user, 'rol') and user.rol else None
    solo_primeros_ciclos = rol_name in [
        'Coordinador de Estudios Generales',
        'Jefe de Estudios Generales'
    ]

    qs = Grupo.objects.para_escuela(escuela, solo_primeros_ciclos=solo_primeros_ciclos)

    # Periodo por defecto
    filter_data = request.GET.copy()
    if not filter_data.get('periodo'):
        periodo_activo = PeriodoAcademico.objects.get_activo()
        if periodo_activo:
            filter_data['periodo'] = periodo_activo.id

    filtro = GrupoFilter(filter_data, queryset=qs, escuela=escuela)  # ← escuela aquí

    grupos = filtro.qs.con_info_completa().annotate(
        vacantes_escuela=Subquery(
            GrupoAsignatura.objects.filter(
                grupo=OuterRef('pk'),
                asignatura__plan__escuela=escuela
            ).values('vacantes')[:1]
        )
    ).distinct().order_by(
        '-periodo__anio',
        'asignatura_base__ciclo',
        'asignatura_base__codigo',
        'numero'
    )

    planes = PlanEstudios.objects.filter(escuela=escuela)
    ciclos = range(1, 3) if solo_primeros_ciclos else range(1, 11)

    context = {
        'grupos'  : grupos,
        'escuela' : escuela,
        'escuelas': escuelas,
        'periodos': PeriodoAcademico.objects.all().order_by('-anio', '-fecha_inicio'),
        'planes'  : planes,
        'ciclos'  : ciclos,
        'filtros' : filter_data,
    }

    return render(request, 'grupos/grupos_list.html', context)

@login_required
def grupo_create(request):
    periodo_activo = _get_periodo_activo_o_redirigir(request)
    if not periodo_activo:
        return redirect('grupos_list')

    if request.method == 'POST':
        form = GrupoForm(request.POST, periodo_activo=periodo_activo, user=request.user)

        if form.is_valid():
            grupo = form.save()

            messages.success(
                request,
                f"¡Grupo {grupo.numero} creado con éxito! Ahora configuremos sus horarios."
            )

            return redirect('grupo_edit', pk=grupo.pk)
        else:
            messages.error(request, "Por favor corrija los errores indicados abajo.")
    else:
        form = GrupoForm(periodo_activo=periodo_activo, user=request.user)

    return render(request, 'grupos/grupo_create.html', {
        'form': form,
        'periodo': periodo_activo,
        'action': 'Crear Nuevo Grupo',
    })


@login_required
def grupo_edit(request, pk):
    user = request.user
    grupo = get_object_or_404(Grupo.objects.para_usuario(user), pk=pk)
    periodo_activo = PeriodoAcademico.objects.get_activo()

    if request.method == 'GET':
        form = GrupoForm(instance=grupo, user=user)
        horario_formset = HorarioFormSet(
            instance=grupo, prefix='horarios', form_kwargs={'user': user}
        )
        vacantes_formset = GrupoAsignaturaFormSet(
            instance=grupo, prefix='vacantes', form_kwargs={'user': user}
        )
        return render(request, 'grupos/grupo_edit.html', {
            'form': form,
            'horario_formset': horario_formset,
            'vacantes_formset': vacantes_formset,
            'grupo': grupo,
            'periodo': periodo_activo,
        })

    if 'add_horario' in request.POST:
        post_data = request.POST.copy()
        post_data['horarios-TOTAL_FORMS'] = int(post_data['horarios-TOTAL_FORMS']) + 1
        fs = HorarioFormSet(
            post_data, instance=grupo, prefix='horarios', form_kwargs={'user': user}
        )
        return render(request, 'grupos/partials/_horarios_formset.html', {
            'horario_formset': fs, 'grupo': grupo
        })

    if 'add_vacante' in request.POST:
        post_data = request.POST.copy()
        post_data['vacantes-TOTAL_FORMS'] = int(post_data['vacantes-TOTAL_FORMS']) + 1
        fs = GrupoAsignaturaFormSet(
            post_data, instance=grupo, prefix='vacantes', form_kwargs={'user': user}
        )
        return render(request, 'grupos/partials/_vacantes_formset.html', {
            'vacantes_formset': fs, 'grupo': grupo
        })

    if '_save_horarios' in request.POST:
        horario_formset = HorarioFormSet(
            request.POST, instance=grupo, prefix='horarios', form_kwargs={'user': user}
        )
        if horario_formset.is_valid():
            with transaction.atomic():
                for f in horario_formset.deleted_forms:
                    if f.instance.pk:
                        f.instance.delete()
                horario_formset.save()
            horario_formset = HorarioFormSet(
                instance=grupo, prefix='horarios', form_kwargs={'user': user}
            )
            return render(request, 'grupos/partials/_horarios_formset.html', {
                'horario_formset': horario_formset,
                'grupo': grupo,
                'exito': 'Horarios guardados correctamente.',
            })
        return render(request, 'grupos/partials/_horarios_formset.html', {
            'horario_formset': horario_formset,
            'grupo': grupo,
            'error': 'Revisa los errores indicados.',
        })

    if '_save_vacantes' in request.POST:
        vacantes_formset = GrupoAsignaturaFormSet(
            request.POST, instance=grupo, prefix='vacantes', form_kwargs={'user': user}
        )
        if vacantes_formset.is_valid():
            with transaction.atomic():
                for f in vacantes_formset.deleted_forms:
                    if f.instance.pk:
                        f.instance.delete()
                vacantes_formset.save()
            vacantes_formset = GrupoAsignaturaFormSet(
                instance=grupo, prefix='vacantes', form_kwargs={'user': user}
            )
            return render(request, 'grupos/partials/_vacantes_formset.html', {
                'vacantes_formset': vacantes_formset,
                'grupo': grupo,
                'exito': 'Vacantes actualizadas correctamente.',
            })
        return render(request, 'grupos/partials/_vacantes_formset.html', {
            'vacantes_formset': vacantes_formset,
            'grupo': grupo,
            'error': 'Revisa los errores indicados.',
        })

    if '_save_main' in request.POST:
        form = GrupoForm(request.POST, instance=grupo, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos del grupo actualizados.')
            return redirect('grupo_edit', pk=grupo.pk)
        # Si falla, recargar el dashboard completo con el form con errores
        horario_formset = HorarioFormSet(
            instance=grupo, prefix='horarios', form_kwargs={'user': user}
        )
        vacantes_formset = GrupoAsignaturaFormSet(
            instance=grupo, prefix='vacantes', form_kwargs={'user': user}
        )
        return render(request, 'grupos/grupo_edit.html', {
            'form': form,
            'horario_formset': horario_formset,
            'vacantes_formset': vacantes_formset,
            'grupo': grupo,
            'periodo': periodo_activo,
        })

    # POST no reconocido
    return HttpResponse(status=400)

@login_required
def grupo_delete(request, pk):
    grupo = get_object_or_404(Grupo.objects.para_usuario(request.user), pk=pk)

    if request.method == 'POST':
        nombre_grupo = str(grupo)
        grupo.delete()
        messages.success(request, f'Grupo {nombre_grupo} eliminado correctamente.')
        return redirect('grupos_list')

    return render(request, 'grupos/grupo_confirm_delete.html', {'grupo': grupo})

@login_required
@transaction.atomic
def grupoasignatura_delete(request, pk):
    """
    Eliminar una asignatura cubierta por un grupo.
    No se puede eliminar la asignatura base.
    """
    ga = get_object_or_404(
        GrupoAsignatura.objects.select_related('grupo', 'asignatura', 'grupo__asignatura_base'),
        pk=pk
    )

    # Verificar permisos sobre el grupo padre
    grupo = get_object_or_404(
        Grupo.objects.para_usuario(request.user),
        pk=ga.grupo_id
    )

    if ga.es_base:
        messages.error(request, "No se puede eliminar la asignatura base del grupo.")
        return redirect('grupo_edit', pk=grupo.pk)

    if request.method == 'POST':
        nombre = str(ga)
        ga.delete()
        messages.success(request, f'Eliminada: {nombre}')
        return redirect('grupo_edit', pk=grupo.pk)

    return render(request, 'grupos/grupoasignatura_confirm_delete.html', {
        'ga': ga,
        'grupo': grupo,
    })

@login_required
def grupo_detail(request, pk):
    user = request.user
    escuelas_permitidas = Escuela.objects.para_usuario(user)

    rol_name = getattr(user.rol, 'name', None) if hasattr(user, 'rol') and user.rol else None
    es_eegg = rol_name in ['Coordinador de Estudios Generales', 'Jefe de Estudios Generales']
    es_vicedecano = rol_name == 'Vicedecano Académico'
    vista_multiple = es_eegg or es_vicedecano

    qs_grupo = Grupo.objects.filter(
        asignaturas__plan__escuela__in=escuelas_permitidas
    ).con_info_completa().distinct()

    if es_eegg:
        qs_grupo = qs_grupo.filter(asignaturas__ciclo__in=[1, 2]).distinct()

    grupo = get_object_or_404(qs_grupo, pk=pk)

    horarios_por_dia = {}
    for horario in grupo.horarios.all():
        dia = horario.get_dia_display()
        if dia not in horarios_por_dia:
            horarios_por_dia[dia] = []
        horarios_por_dia[dia].append(horario)

    qs_asignaturas = grupo.asignaturas_cubiertas.select_related(
        'asignatura',
        'asignatura__plan',
        'asignatura__plan__escuela',
    )

    if vista_multiple:
        if es_eegg:
            qs_asignaturas = qs_asignaturas.filter(asignatura__ciclo__in=[1, 2])
        asignaturas_cubiertas = qs_asignaturas
        asignatura_display = grupo.asignatura_base
    else:
        asignaturas_cubiertas = qs_asignaturas.filter(
            asignatura__plan__escuela__in=escuelas_permitidas
        ).order_by('asignatura__plan__escuela__nombre')
        primera = asignaturas_cubiertas.first()
        asignatura_display = primera.asignatura if primera else grupo.asignatura_base

    context = {
        'grupo': grupo,
        'horarios_por_dia': horarios_por_dia,
        'asignaturas_cubiertas': asignaturas_cubiertas,
        'asignatura_display': asignatura_display,
        'vista_multiple': vista_multiple,
    }

    return render(request, 'grupos/grupo_detail.html', context)

@login_required
def importar_grupos_view(request):
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            archivo = request.FILES['archivo']
            periodo = form.cleaned_data['periodo']
            escuela = form.cleaned_data['escuela']

            try:
                # Pasamos el periodo a la función
                resultado = importar_programacion(archivo, request.user, periodo, escuela)

                return render(request, 'grupos/importar_resultado.html', {
                    'creados': resultado['creados'],
                    'errores': resultado['errores']
                })

            except ExcelImportError as e:
                form.add_error(None, str(e))
            except Exception as e:
                form.add_error(None, f"Error crítico: {str(e)}")
    else:
        form = UploadExcelForm(user=request.user)

    return render(request, 'grupos/importar_form.html', {'form': form})
