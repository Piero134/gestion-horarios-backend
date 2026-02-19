from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Value
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
from .filters import GrupoFilter
from .utils.exporter import generar_reporte_grupos
from .utils.importer import importar_programacion, ExcelImportError
from .excel_forms import UploadExcelForm

@login_required
def grupos_list(request):
    """Lista de grupos con filtros"""

    filter_data = request.GET.copy()

    if not filter_data.get('periodo'):
        periodo_activo = PeriodoAcademico.objects.get_activo()
        if periodo_activo:
            filter_data['periodo'] = periodo_activo.id

    qs = Grupo.objects.para_usuario(request.user)

    filtro = GrupoFilter(filter_data, queryset=qs)

    grupos = filtro.qs.con_info_completa().annotate(
        total_vacantes_db=Coalesce(Sum('vacantes__cantidad'), Value(0))
    ).order_by(
        '-periodo__anio',
        'asignatura__ciclo',
        'asignatura__codigo',
        'numero'
    )

    paginator = Paginator(grupos, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    user = request.user
    escuelas = Escuela.objects.none()
    planes = PlanEstudios.objects.none()

    if hasattr(user, 'rol') and user.rol.name == 'Vicedecano Académico':
        escuelas = Escuela.objects.filter(facultad=user.facultad).order_by('codigo')

    escuela_id = filter_data.get('escuela')
    if escuela_id and str(escuela_id).isdigit():
        planes = PlanEstudios.objects.filter(escuela_id=escuela_id)
    elif hasattr(user, 'escuela') and user.escuela:
        planes = PlanEstudios.objects.filter(escuela=user.escuela)

    ciclos = range(1, 11)

    if hasattr(user, 'rol') and user.rol.name in [
        "Coordinador de Estudios Generales",
        "Jefe de Estudios Generales"
    ]:
        ciclos = range(1, 3)

    context = {
        'grupos': page_obj,
        'filtros': filter_data,
        'periodos': PeriodoAcademico.objects.all().order_by('-anio', '-fecha_inicio'),
        'escuelas': escuelas,
        'planes': planes.order_by('nombre'),
        'ciclos': ciclos,
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

        horario_formset = HorarioFormSet(request.POST, instance=grupo, prefix='horarios')

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

    grupo = get_object_or_404(Grupo.objects.para_usuario(request.user), pk=pk)

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
        Grupo.objects.para_usuario(request.user).con_info_completa(),
        pk=pk
    )

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
def importar_grupos_view(request):
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']

            try:
                resultado = importar_programacion(archivo, request.user)

                # Feedback al usuario
                creados = resultado['creados']
                errores = resultado['errores']

                return render(request, 'grupos/importar_resultado.html', {
                    'creados': creados,
                    'errores': errores
                })

            except ExcelImportError as e:
                form.add_error(None, f"Error en el formato del Excel: {str(e)}")
            except Exception as e:
                form.add_error(None, f"Error interno: {str(e)}")

    else:
        form = UploadExcelForm()

    return render(request, 'grupos/importar_form.html', {'form': form})
