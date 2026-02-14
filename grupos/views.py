from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Value, Q
from django.core.paginator import Paginator
from grupos.models import Grupo
from grupos.forms import (
    GrupoForm,
    HorarioFormSet,
    DistribucionVacantesFormSet,
)
from periodos.models import PeriodoAcademico
from escuelas.models import Escuela
from planes.models import PlanEstudios
from django.db.models.functions import Coalesce
from django.http import HttpResponse, Http404
from .exporter import generar_reporte_grupos

@login_required
def grupos_list(request):
    """Lista de grupos con filtros"""

    # Obtener filtros
    periodo_id = request.GET.get('periodo')
    escuela_id = request.GET.get('escuela')
    plan_id = request.GET.get('plan')
    ciclo = request.GET.get('ciclo')
    grupo_num = request.GET.get('grupo')
    buscar = request.GET.get('buscar', '').strip()
    page_number = request.GET.get('page')

    # Base queryset según rol
    user = request.user

    grupos = Grupo.objects.para_usuario(user)

    escuelas_para_filtro = Escuela.objects.none()
    if hasattr(user, 'rol') and user.rol.name == 'Vicedecano Académico':
        escuelas_para_filtro = Escuela.objects.filter(facultad=user.facultad).order_by('codigo')

    planes_para_filtro = PlanEstudios.objects.none()
    if escuela_id and escuela_id.isdigit():
        planes_para_filtro = PlanEstudios.objects.filter(escuela_id=escuela_id)
    elif hasattr(user, 'escuela') and user.escuela:
        planes_para_filtro = PlanEstudios.objects.filter(escuela=user.escuela)

    # Aplicar filtros
    if periodo_id and periodo_id.isdigit():
        grupos = grupos.filter(periodo_id=periodo_id)
    else:
        # Por defecto: Periodo Activo
        periodo_activo = PeriodoAcademico.objects.get_activo()
        if periodo_activo:
            grupos = grupos.filter(periodo=periodo_activo)
            periodo_id = periodo_activo.id

    if escuela_id and str(escuela_id).isdigit() and user.rol.name == 'Vicedecano Académico':
        grupos = grupos.filter(asignatura__plan__escuela_id=escuela_id)

    if plan_id and plan_id.isdigit():
        grupos = grupos.filter(asignatura__plan_id=plan_id)

    if ciclo and ciclo.isdigit():
        grupos = grupos.filter(asignatura__ciclo=ciclo)

    if grupo_num and grupo_num.isdigit():
        grupos = grupos.filter(numero=grupo_num)

    if buscar:
        grupos = grupos.filter(
            Q(asignatura__codigo__icontains=buscar) |
            Q(asignatura__nombre__icontains=buscar) |
            Q(docente__apellido__icontains=buscar) |
            Q(docente__nombre__icontains=buscar)
        )

    grupos = grupos.select_related(
        'asignatura',
        'asignatura__plan',
        'asignatura__plan__escuela',
        'periodo',
        'docente'
    ).prefetch_related(
        'horarios',
    ).annotate(
        total_vacantes_db=Coalesce(Sum('vacantes__cantidad'), Value(0))
    ).order_by(
        '-periodo__anio',
        'asignatura__ciclo',
        'asignatura__codigo',
        'numero'
    )

    paginator = Paginator(grupos, 20) # 20 items por página
    page_obj = paginator.get_page(page_number)

    context = {
        'grupos': page_obj,

        # Datos para llenar los <select>
        'periodos': PeriodoAcademico.objects.all().order_by('-anio', '-fecha_inicio'),
        'escuelas': escuelas_para_filtro,
        'planes': planes_para_filtro.order_by('nombre'),
        'ciclos': range(1, 11),

        # Estado actual de los filtros (para mantener seleccionado en el HTML)
        'filtros': {
            'periodo': int(periodo_id) if periodo_id else '',
            'escuela': int(escuela_id) if escuela_id and str(escuela_id).isdigit() else '',
            'plan': int(plan_id) if plan_id and str(plan_id).isdigit() else '',
            'ciclo': int(ciclo) if ciclo and str(ciclo).isdigit() else '',
            'grupo': grupo_num if grupo_num else '',
            'buscar': buscar
        }
    }

    return render(request, 'grupos/grupos_list.html', context)


@login_required
@transaction.atomic
def grupo_create(request):
    periodo_activo = PeriodoAcademico.objects.get_activo()

    if not periodo_activo:
        return render(request, 'grupos/error_no_periodo.html', {
            'mensaje': 'No existe un periodo académico activo actualmente. Contacte al administrador.'
        })

    if request.method == 'POST':
        form = GrupoForm(request.POST, periodo_activo=periodo_activo, user=request.user)
        horario_formset = HorarioFormSet(request.POST, prefix='horarios')
        vacantes_formset = DistribucionVacantesFormSet(request.POST, prefix='vacantes')

        if form.is_valid():
            try:
                with transaction.atomic():
                # Primero guardar el grupo para obtener el pk
                    grupo = form.save()

                    vacantes_formset.instance = grupo
                    if vacantes_formset.is_valid():
                        vacantes_formset.save()
                    else:
                        raise ValueError("Error en vacantes")

                    horario_formset.instance = grupo
                    if horario_formset.is_valid():
                        horario_formset.save()
                    else:
                         raise ValueError("Error en horarios")

                messages.success(request, f"Grupo {grupo} creado exitosamente en {periodo_activo}.")
                return redirect('grupo_detail', pk=grupo.pk)

            except ValueError as e:
                messages.error(request, f"Por favor corrija los errores: {str(e)}")

        else:
            print("🔴 ERRORES DEL FORM:", form.errors)
            print("🔴 DATA RECIBIDA:", request.POST)
            messages.error(request, "Error en el formulario principal.")

    else:
        form = GrupoForm(periodo_activo=periodo_activo, user=request.user)
        vacantes_formset = DistribucionVacantesFormSet(prefix='vacantes')
        horario_formset = HorarioFormSet(prefix='horarios')

    context = {
        'form': form,
        'vacantes_formset': vacantes_formset,
        'horario_formset': horario_formset,
        'periodo': periodo_activo
    }
    return render(request, 'grupos/grupo_form.html', context)


@login_required
@transaction.atomic
def grupo_edit(request, pk):
    grupo = get_object_or_404(Grupo.objects.para_usuario(request.user), pk=pk)

    user = request.user

    if request.method == 'POST':
        form = GrupoForm(request.POST, instance=grupo, user=user)

        horario_formset = HorarioFormSet(request.POST, instance=grupo)

        # MAGIA AQUÍ: Pasamos el 'user' a todos los sub-formularios del formset
        vacantes_formset = DistribucionVacantesFormSet(
            request.POST,
            instance=grupo,
            form_kwargs={'user': user}
        )

        if form.is_valid() and horario_formset.is_valid() and vacantes_formset.is_valid():
            try:
                # Guardar Grupo
                grupo = form.save()

                # Guardar FormSets
                horario_formset.save()
                vacantes_formset.save()

                messages.success(request, f'Grupo {grupo} actualizado exitosamente.')
                return redirect('grupo_detail', pk=grupo.pk)

            except Exception as e:
                # Captura errores inesperados de base de datos
                messages.error(request, f'Error al actualizar el grupo: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')

            # Opcional: Imprimir errores en consola para depurar si algo falla silenciosamente
            # print(form.errors, horario_formset.errors, vacantes_formset.errors)

    else:
        # 4. Cargar datos existentes (GET)
        form = GrupoForm(instance=grupo, user=user)
        horario_formset = HorarioFormSet(instance=grupo)
        vacantes_formset = DistribucionVacantesFormSet(
            instance=grupo,
            form_kwargs={'user': user}
        )

    context = {
        'form': form, # Usamos 'form' genérico como espera tu template
        'horario_formset': horario_formset,
        'vacantes_formset': vacantes_formset,
        'grupo': grupo, # Para mostrar datos en el header o breadcrumbs
        'action': 'Editar'
    }

    return render(request, 'grupos/grupo_form.html', context)


@login_required
def grupo_delete(request, pk):
    """Eliminar grupo"""

    grupo = get_object_or_404(Grupo, pk=pk)

    # Verificar permisos
    if request.user.rol.name == 'Vicedecano Académico':
        if grupo.asignatura.plan.escuela.facultad != request.user.facultad:
            messages.error(request, 'No tiene permisos para eliminar este grupo.')
            return redirect('grupos_list')
    else:
        if request.user.escuela and grupo.asignatura.plan.escuela != request.user.escuela:
            messages.error(request, 'No tiene permisos para eliminar este grupo.')
            return redirect('grupos_list')

    if request.method == 'POST':
        nombre_grupo = str(grupo)
        grupo.delete()
        messages.success(request, f'Grupo {nombre_grupo} eliminado correctamente.')
        return redirect('grupos_list')

    context = {
        'grupo': grupo
    }

    return render(request, 'grupos/grupo_confirm_delete.html', context)


@login_required
def grupo_detail(request, pk):
    """Detalle de grupo"""

    grupo = get_object_or_404(
        Grupo.objects.select_related(
            'asignatura',
            'asignatura__plan',
            'asignatura__plan__escuela',
            'periodo',
            'docente'
        ).prefetch_related('horarios', 'vacantes', 'vacantes__asignatura'),
        pk=pk
    )

    # Verificar permisos
    if request.user.rol.name == 'Vicedecano Académico':
        if grupo.asignatura.plan.escuela.facultad != request.user.facultad:
            messages.error(request, 'No tiene permisos para ver este grupo.')
            return redirect('grupos_list')
    else:
        if request.user.escuela and grupo.asignatura.plan.escuela != request.user.escuela:
            messages.error(request, 'No tiene permisos para ver este grupo.')
            return redirect('grupos_list')

    # Organizar horarios por día
    horarios_por_dia = {}
    for horario in grupo.horarios.all():
        dia = horario.get_dia_display()
        if dia not in horarios_por_dia:
            horarios_por_dia[dia] = []
        horarios_por_dia[dia].append(horario)

    context = {
        'grupo': grupo,
        'horarios_por_dia': horarios_por_dia,
    }

    return render(request, 'grupos/grupo_detail.html', context)

@login_required
def grupo_export_excel(request):
    periodo_id = request.GET.get('periodo_id')

    archivo_excel, nombre_archivo = generar_reporte_grupos(periodo_id=periodo_id, user=request.user)

    if not archivo_excel:
        raise Http404("No se encontraron datos para generar el reporte o no tiene permisos.")

    response = HttpResponse(
        archivo_excel,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'

    return response
