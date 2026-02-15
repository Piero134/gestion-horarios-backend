import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

class UnmsmScraperService:
    URL_FUENTE = "https://sum.unmsm.edu.pe/pregrado.htm"

    # Mapeo de meses en español para conversión
    MESES = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
        'julio': 7, 'agosto': 8, 'setiembre': 9, 'septiembre': 9, 'octubre': 10,
        'noviembre': 11, 'diciembre': 12
    }

    @classmethod
    def parse_fecha_espanol(cls, dia_str, mes_str, anio_referencia):
        """Convierte '08', 'enero', 2026 -> objeto date(2026, 1, 8)"""
        try:
            dia = int(dia_str)
            mes = cls.MESES.get(mes_str.lower())
            if not mes:
                return None
            return datetime(anio_referencia, mes, dia).date()
        except ValueError:
            return None

    @classmethod
    def obtener_periodos(cls):
        print(f"Conectando a {cls.URL_FUENTE}...")
        try:
            # Desactivamos verificación SSL temporalmente si el certificado de la UNMSM falla (común en webs del estado)
            response = requests.get(cls.URL_FUENTE, verify=False, timeout=15)
            response.encoding = 'utf-8' # Forzar UTF-8 para tildes
        except Exception as e:
            print(f"Error de conexión: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        periodos_encontrados = []

        # Iteramos sobre todas las filas de las tablas (tr)
        # Buscamos filas que contengan la palabra "Clases" en la columna de ACTIVIDAD
        filas = soup.find_all('tr')

        # Variables de estado para rastrear en qué periodo estamos mientras bajamos por la tabla
        periodo_actual_nombre = None
        anio_actual = datetime.now().year # Fecha de referencia para interpretar años

        for fila in filas:
            celdas = fila.find_all(['td', 'th'])
            # texto de la fila sin etiquetas, para buscar patrones
            texto_fila = fila.get_text(" ", strip=True)

            # Buscamos patrones "(Verano|Semestre|Anual) (4 digitos) (-I|-II)?"
            match_nombre = re.search(r'(VERANO|SEMESTRE|ANUAL)\s+(\d{4})[-–]?([0I]{1,2})?', texto_fila, re.IGNORECASE)
            if match_nombre:
                # Actualizamos el contexto del periodo actual
                raw_nombre = match_nombre.group(0) # Patron encontrado (completo)
                anio_actual = int(match_nombre.group(2)) # Año encontrado

                # Normalizamos nombre para la BD
                if "VERANO" in raw_nombre.upper():
                    periodo_actual_nombre = f"{anio_actual}-0" # 2026-0
                elif "ANUAL" in raw_nombre.upper():
                    periodo_actual_nombre = f"{anio_actual}-A" # 2026-A (Anual)
                else:
                    # Semestre
                    sufijo = match_nombre.group(3) if match_nombre.group(3) else ""
                    periodo_actual_nombre = f"{anio_actual}-{sufijo}" # 2026-I

            if "Clases" in texto_fila and "Inicio:" in texto_fila:
                if not periodo_actual_nombre:
                    continue # No sabemos a qué periodo pertenece esta fila

                # Patron para extraer fechas: "Inicio: 08 de enero ... Término: 15 de julio"
                patron_fechas = r"Inicio:.*?\s(\d{1,2})\sde\s([a-z]+).*?Término:.*?\s(\d{1,2})\sde\s([a-z]+)"
                match_fechas = re.search(patron_fechas, texto_fila, re.IGNORECASE | re.DOTALL)

                if match_fechas:
                    # Desglosamos las partes de la fecha
                    ini_dia, ini_mes, fin_dia, fin_mes = match_fechas.groups()

                    # Interpretamos las fechas usando el año de referencia actual
                    fecha_inicio = cls.parse_fecha_espanol(ini_dia, ini_mes, anio_actual)

                    # Para la fecha de fin, hay casos donde el año puede ser el siguiente (ej: inicio en agosto y fin en enero)
                    anio_fin = anio_actual
                    fecha_fin = cls.parse_fecha_espanol(fin_dia, fin_mes, anio_fin)

                    # Corrección de año nuevo: si inicio es mes 8 y fin es mes 1, fin es año+1
                    if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
                        fecha_fin = cls.parse_fecha_espanol(fin_dia, fin_mes, anio_fin + 1)

                    if fecha_inicio and fecha_fin:
                        # Determinar tipo para el modelo
                        tipo_modelo = 'SEMESTRE'
                        if '-0' in periodo_actual_nombre: tipo_modelo = 'VERANO'
                        if '-A' in periodo_actual_nombre: tipo_modelo = 'ANUAL'

                        periodos_encontrados.append({
                            'nombre': periodo_actual_nombre,
                            'tipo': tipo_modelo,
                            'anio': anio_actual,
                            'fecha_inicio': fecha_inicio,
                            'fecha_fin': fecha_fin,
                            'fuente_oficial': cls.URL_FUENTE
                        })

        return periodos_encontrados
