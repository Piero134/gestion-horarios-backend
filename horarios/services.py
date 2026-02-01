from datetime import datetime
from .models import Horario


def detectar_conflictos_horarios(grupos_ids, periodo_id=None):
    # Obtener horarios de los grupos seleccionados
    horarios_query = Horario.objects.select_related(
        'grupo', 'grupo__asignatura', 'aula'
    ).filter(grupo_id__in=grupos_ids)
    
    if periodo_id:
        horarios_query = horarios_query.filter(grupo__periodo_id=periodo_id)
    
    horarios_lista = list(horarios_query.order_by('dia', 'hora_inicio'))
    
    # Detectar conflictos
    conflictos = []
    for i, h1 in enumerate(horarios_lista):
        for h2 in horarios_lista[i+1:]:
            # Mismo día
            if h1.dia == h2.dia:
                # Horarios se solapan
                if not (h1.hora_fin <= h2.hora_inicio or h2.hora_fin <= h1.hora_inicio):
                    conflictos.append({
                        'tipo': 'conflicto_horario',
                        'horario1': {
                            'grupo': h1.grupo.nombre,
                            'asignatura': h1.grupo.asignatura.nombre,
                            'dia': h1.get_dia_display(),
                            'hora_inicio': h1.hora_inicio.strftime('%H:%M'),
                            'hora_fin': h1.hora_fin.strftime('%H:%M')
                        },
                        'horario2': {
                            'grupo': h2.grupo.nombre,
                            'asignatura': h2.grupo.asignatura.nombre,
                            'dia': h2.get_dia_display(),
                            'hora_inicio': h2.hora_inicio.strftime('%H:%M'),
                            'hora_fin': h2.hora_fin.strftime('%H:%M')
                        },
                        'mensaje': f"Conflicto el {h1.get_dia_display()} entre {h1.hora_inicio.strftime('%H:%M')}-{h1.hora_fin.strftime('%H:%M')}"
                    })
    
    return {
        'tiene_conflictos': len(conflictos) > 0,
        'cantidad_conflictos': len(conflictos),
        'conflictos': conflictos
    }
