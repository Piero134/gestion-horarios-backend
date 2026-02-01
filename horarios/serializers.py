def serializar_periodo(periodo):
    # Convierte un PeriodoAcademico a JSON.
    return {
        'id': periodo.id,
        'nombre': periodo.nombre,
        'tipo': periodo.tipo,
        'anio': periodo.anio,
        'fecha_inicio': periodo.fecha_inicio.isoformat(),
        'fecha_fin': periodo.fecha_fin.isoformat(),
        'activo': periodo.activo
    }


def serializar_asignatura(asignatura):
    # Convierte una Asignatura a JSON.
    return {
        'id': asignatura.id,
        'codigo': asignatura.codigo,
        'nombre': asignatura.nombre,
        'ciclo': asignatura.ciclo,
        'tipo': asignatura.tipo,
        'creditos': asignatura.creditos,
        'horas_teoria': asignatura.horas_teoria,
        'horas_practica': asignatura.horas_practica,
        'horas_laboratorio': asignatura.horas_laboratorio,
        'plan_id': asignatura.plan.id if asignatura.plan else None,
        'escuela': asignatura.plan.escuela.nombre if asignatura.plan and asignatura.plan.escuela else None
    }


def serializar_docente(docente):
    # Convierte un Docente a JSON.
    if not docente:
        return None
    return {
        'id': docente.id,
        'nombre': docente.nombre,
        'apellido': docente.apellido,
        'nombre_completo': f"{docente.nombre} {docente.apellido}",
        'email': docente.email
    }


def serializar_aula(aula):
    # Convierte un Aula a JSON.
    return {
        'id': aula.id,
        'nombre': aula.nombre,
        'capacidad': aula.capacidad,
        'es_laboratorio': aula.es_laboratorio
    }


def serializar_horario(horario):
    # Convierte un Horario a JSON.
    return {
        'id': horario.id,
        'grupo_id': horario.grupo.id,
        'tipo': horario.tipo,
        'tipo_display': horario.get_tipo_display(),
        'dia': horario.dia,
        'dia_display': horario.get_dia_display(),
        'hora_inicio': horario.hora_inicio.strftime('%H:%M'),
        'hora_fin': horario.hora_fin.strftime('%H:%M'),
        'aula': serializar_aula(horario.aula)
    }


def serializar_grupo(grupo, incluir_horarios=False):
    # Convierte un Grupo a JSON.
    data = {
        'id': grupo.id,
        'nombre': grupo.nombre,
        'asignatura': serializar_asignatura(grupo.asignatura),
        'periodo': serializar_periodo(grupo.periodo),
        'docente': serializar_docente(grupo.docente),
        'total_vacantes': grupo.total_vacantes
    }
    
    if incluir_horarios:
        data['horarios'] = [
            serializar_horario(horario)
            for horario in grupo.horarios.all().order_by('dia', 'hora_inicio')
        ]
    
    return data
