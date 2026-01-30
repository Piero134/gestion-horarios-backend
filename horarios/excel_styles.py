from datetime import datetime, time, timedelta
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side


class ExcelEstilos:
    # Colores
    COLOR_CABECERA = "FFD966"  # Amarillo
    COLOR_HORA = "E7E6E6"      # Gris claro
    COLOR_TEORIA = "CCCCFF"    # Azul claro
    COLOR_PRACTICA = "FFE699"  # Naranja claro
    COLOR_LABORATORIO = "C6E0B4"  # Verde claro
    
    # Fuentes
    FONT_CABECERA = Font(name='Arial', size=11, bold=True)
    FONT_TITULO = Font(name='Arial', size=14, bold=True)
    FONT_NORMAL = Font(name='Arial', size=10)
    FONT_SMALL = Font(name='Arial', size=9)
    
    # Alineaciones
    ALIGN_CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ALIGN_LEFT = Alignment(horizontal='left', vertical='center', wrap_text=True)
    
    # Bordes
    BORDER_THIN = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    @staticmethod
    def get_color_tipo(tipo):
        # Retorna el color según el tipo de sesión.
        if tipo == 'T':
            return ExcelEstilos.COLOR_TEORIA
        elif tipo == 'P':
            return ExcelEstilos.COLOR_PRACTICA
        elif tipo == 'L':
            return ExcelEstilos.COLOR_LABORATORIO
        return "FFFFFF"


def crear_rango_horas(hora_inicio=time(8, 0), hora_fin=time(22, 0), intervalo_minutos=60):
    # Crea una lista de rangos de horas.
    horas = []
    hora_actual = datetime.combine(datetime.today(), hora_inicio)
    hora_limite = datetime.combine(datetime.today(), hora_fin)
    
    while hora_actual < hora_limite:
        hora_siguiente = hora_actual + timedelta(minutes=intervalo_minutos)
        horas.append({
            'inicio': hora_actual.time(),
            'fin': hora_siguiente.time(),
            'texto': f"{hora_actual.strftime('%H:%M')}"
        })
        hora_actual = hora_siguiente
    
    return horas


def aplicar_estilo_celda(celda, texto, font=None, fill=None, alignment=None, border=None):
    # Aplica estilo a una celda.
    try:
        celda.value = texto
    except AttributeError:
        # La celda está merged, solo aplicar estilos
        pass
    
    if font:
        celda.font = font
    if fill:
        celda.fill = fill
    if alignment:
        celda.alignment = alignment
    if border:
        celda.border = border


def generar_color_asignatura(nombre_asignatura):
    # Paleta de colores predefinida (colores pastel legibles)
    paleta_colores = [
        "B8CCE4",  # Azul claro
        "FFE699",  # Amarillo pastel
        "C6E0B4",  # Verde claro
        "F4B084",  # Naranja claro
        "D5A6BD",  # Rosa claro
        "BDD7EE",  # Azul cielo
        "C5E0DC",  # Verde agua
        "F8CBAD",  # Durazno
        "E2EFDA",  # Verde menta
        "FCE4D6",  # Crema
        "DDEBF7",  # Azul bebé
        "FFF2CC",  # Amarillo pálido
        "D9E1F2",  # Lavanda
        "E2F0D9",  # Verde lima claro
        "FBE5D6",  # Albaricoque
    ]
    
    # Usar hash para seleccionar un color de la paleta
    hash_value = hash(nombre_asignatura)
    indice = abs(hash_value) % len(paleta_colores)
    
    return paleta_colores[indice]
