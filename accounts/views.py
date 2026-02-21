from django.shortcuts import render
<<<<<<< HEAD
from django.db.models import Count, Sum, Q
from django.utils import timezone
from periodos.models import PeriodoAcademico
from grupos.models import Grupo, DistribucionVacantes
from escuelas.models import Escuela
from aulas.models import Aula
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    # Periodo activo o mas reciente
    hoy = timezone.now().date()
    periodo_actual = PeriodoAcademico.objects.filter(
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy
    ).first()

    if not periodo_actual:
        # Si no hay periodo mostramos el ultimo
        periodo_actual = PeriodoAcademico.objects.order_by('-anio', '-fecha_inicio').first()

    context = {
        'periodo': periodo_actual,
        'kpi': {
            'total_grupos': 0,
            'grupos_sin_horario': 0,
            'conflictos_estimados': 0,
            'porcentaje_avance': 0,
            'total_vacantes': 0,
            'matriculados': 0,
            'ocupacion_aulas': 0
        }
    }

    if periodo_actual:
        # Total de grupos en la facultad
        grupos = Grupo.objects.filter(periodo = periodo_actual,
            asignatura__plan__escuela__facultad_id=1
        ).select_related('asignatura__plan')\
        .only('numero', 'asignatura__nombre', 'asignatura__plan__nombre')
        total_grupos = grupos.count()

        # Grupos sin horario asignado
        grupos_sin_horario = grupos.annotate(num_horarios=Count('horarios')).filter(num_horarios=0).count()

        # Porcentaje de avance en asignación de horarios
        if total_grupos > 0:
            avance = ((total_grupos - grupos_sin_horario) / total_grupos) * 100
        else:
            avance = 0

        # Vacantes y matriculados
        stats_vacantes = DistribucionVacantes.objects.filter(grupo__periodo=periodo_actual).aggregate(
            total_oferta=Sum('cantidad'),
            total_inscritos=Sum('matriculados')
        )

        # Aulas usadas y totales
        aulas_totales = Aula.objects.count()
        aulas_usadas = Aula.objects.filter(horarios__grupo__periodo=periodo_actual).distinct().count()

        context['kpi'].update({
            'total_grupos': total_grupos,
            'grupos_sin_horario': grupos_sin_horario,
            'porcentaje_avance': round(avance, 1),
            'total_vacantes': stats_vacantes['total_oferta'] or 0,
            'matriculados': stats_vacantes['total_inscritos'] or 0,
            'aulas_activas': aulas_usadas,
            'total_aulas': aulas_totales
        })

        # Datos para graficos
        vacantes_por_escuela = []
        escuelas = Escuela.objects.filter(facultad = request.user.facultad)
        for escuela in escuelas:
            cantidad = DistribucionVacantes.objects.filter(
                grupo__periodo=periodo_actual,
                grupo__asignatura__plan__escuela=escuela
            ).aggregate(total=Sum('cantidad'))['total'] or 0

            vacantes_por_escuela.append({
                'nombre': escuela.nombre,
                'cantidad': cantidad
            })

        context['chart_data'] = vacantes_por_escuela

    return render(request, 'home.html', context)
=======

# Create your views here.
def login_page(request):
    return render(request,'login.html')

def register_page(request):
    return render(request,'register.html')

def dashboard_page(request):
    return render(request,'dashboard.html')
>>>>>>> 71224ecb86f8f8c385092b501f3124b34fd8718b
