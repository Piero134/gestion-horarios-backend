import re
from datetime import time

from aulas.models import Aula
from docentes.models import Docente


def limpiar_texto(texto):
    """Limpia y normaliza texto extraído de Excel."""
    if texto is None:
        return ""
    return str(texto).strip()


def interpretar_dia(dia_texto):
    """Convierte el nombre del día a número (1-7)."""
    dias_map = {
        'LUNES': 1, '1LUNES': 1,
        'MARTES': 2, '2MARTES': 2,
        'MIERCOLES': 3, 'MIÉRCOLES': 3, '3MIERCOLES': 3, '3MIÉRCOLES': 3,
        'JUEVES': 4, '4JUEVES': 4,
        'VIERNES': 5, '5VIERNES': 5,
        'SABADO': 6, 'SÁBADO': 6, '6SABADO': 6, '6SÁBADO': 6,
        'DOMINGO': 7, '7DOMINGO': 7,
    }
    dia_limpio = limpiar_texto(dia_texto).upper().replace(' ', '')
    return dias_map.get(dia_limpio, None)


def interpretar_hora(hora_texto):
    """Convierte texto de hora a objeto time."""
    if isinstance(hora_texto, time):
        return hora_texto
    
    hora_str = limpiar_texto(hora_texto)
    # Formato HH:MM
    match = re.match(r'(\d{1,2}):(\d{2})', hora_str)
    if match:
        hora, minuto = int(match.group(1)), int(match.group(2))
        return time(hora, minuto)
    
    return None


def interpretar_tipo_sesion(tipo_texto):
    """Convierte el tipo de sesión a la clave correspondiente."""
    tipo_map = {
        'T': 'T', 'TEORIA': 'T', 'TEORÍA': 'T',
        'P': 'P', 'PRACTICA': 'P', 'PRÁCTICA': 'P',
        'L': 'L', 'LABORATORIO': 'L', 'LAB': 'L',
    }
    tipo_limpio = limpiar_texto(tipo_texto).upper()
    return tipo_map.get(tipo_limpio, 'T')


def obtener_o_crear_aula(nombre_aula, es_laboratorio=False):
    """Obtiene o crea un aula."""
    aula, created = Aula.objects.get_or_create(
        nombre=nombre_aula,
        defaults={
            'capacidad': 40,  # Capacidad por defecto
            'es_laboratorio': es_laboratorio
        }
    )
    return aula


def obtener_o_crear_docente(nombre_completo):
    """Obtiene o crea un docente a partir de su nombre completo."""
    if not nombre_completo:
        return None
    
    partes = nombre_completo.strip().split()
    if len(partes) >= 2:
        nombre = ' '.join(partes[:-1])
        apellido = partes[-1]
    else:
        nombre = nombre_completo
        apellido = ""
    
    email = f"{apellido.lower()}@unmsm.edu.pe"
    
    docente, created = Docente.objects.get_or_create(
        nombre=nombre,
        apellido=apellido,
        defaults={'email': email}
    )
    return docente
