from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
import io
from django.http import JsonResponse
from .models import PeriodoAcademico

# --- LISTAR PERIODOS ---
@login_required
def periodo_list(request):
    """Muestra la lista de periodos y el botón de sincronización."""
    periodos = PeriodoAcademico.objects.all().order_by('-anio', '-fecha_inicio')

    context = {
        'periodos': periodos,
        'titulo': 'Periodos Académicos'
    }
    return render(request, 'periodos/periodo_list.html', context)

# --- ACCIÓN: EJECUTAR COMANDO ---
@login_required
# @user_passes_test(lambda u: u.is_staff)  # Descomenta si solo admins pueden usarlo
def sincronizar_periodos_view(request):
    if request.method == 'POST':
        try:
            out = io.StringIO()
            # Ejecuta el comando
            call_command('sincronizar_periodos', stdout=out)
            resultado = out.getvalue()

            # Devuelve JSON con éxito
            return JsonResponse({
                'status': 'success',
                'message': 'Sincronización completada.' # Mensaje corto estilo imagen
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f"Error: {str(e)}"
            }, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
