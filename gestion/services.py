from .models import Horario,Ciclo,Curso

class HorarioService:
    @staticmethod
    def obtener_horario_estructurado(grupo_id,ciclo_id):
        horarios = Horario.objects.filter(
            grupo_id=grupo_id,
            curso__ciclo__numero=ciclo_id
        ).select_related('curso', 'docente', 'aula', 'grupo').order_by('dia_semana', 'hora_inicio')

        if not horarios:
            return None

        nombres_dias = dict(Horario.DIAS_OPCIONES)

        dias_agrupados = {}
        for h in horarios:
            nombre_dia = nombres_dias.get(h.dia_semana, h.dia_semana)
            
            if nombre_dia not in dias_agrupados:
                dias_agrupados[nombre_dia] = []
            
            # Añadimos la clase al día correspondiente
            dias_agrupados[nombre_dia].append({
                "curso": h.curso.nombre,
                "docente": h.docente.nombre,
                "aula": h.aula.numero,
                "tipo_clase": h.tipo_clase.nombre,
                "hora_inicio": h.hora_inicio.strftime('%H:%M'), 
                "hora_fin": h.hora_fin.strftime('%H:%M')
            })

        lista_dias = []
        for nombre_dia, clases in dias_agrupados.items():
            lista_dias.append({
                "dia": nombre_dia,
                "clases": clases
            })

        resultado_final = {
            "ciclo": ciclo_id,
            "grupo": str(horarios[0].grupo.numero),
            "horarios": [
                {
                    "dias": lista_dias
                }
            ]
        }

        return resultado_final