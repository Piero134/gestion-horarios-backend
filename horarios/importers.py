from datetime import datetime
import re
from openpyxl import load_workbook

from asignaturas.models import Asignatura
from grupos.models import Grupo, DistribucionVacantes
from periodos.models import PeriodoAcademico
from .models import Horario
from .utils import (
    limpiar_texto,
    interpretar_dia,
    interpretar_hora,
    interpretar_tipo_sesion,
    obtener_o_crear_aula,
    obtener_o_crear_docente
)


def importar_horarios_desde_excel(archivo_excel, periodo_id=None):
    # Cargar el archivo Excel
    if isinstance(archivo_excel, str):
        workbook = load_workbook(archivo_excel)
    else:
        workbook = load_workbook(archivo_excel)
    
    # Obtener periodo académico
    if periodo_id:
        periodo = PeriodoAcademico.objects.get(id=periodo_id)
    else:
        # Intentar extraer el periodo de la primera fila del Excel
        periodo = None
        primera_hoja = workbook[workbook.sheetnames[0]]
        primera_celda = primera_hoja['A1'].value
        
        if primera_celda:
            # Buscar patrón "PROGRAMACIÓN ACADÉMICA YYYY-N" o similar
            texto_celda = limpiar_texto(primera_celda).upper()
            patron_periodo = re.search(r'(\d{4})[-‐](I|II|1|2)', texto_celda)
            
            if patron_periodo:
                anio = int(patron_periodo.group(1))
                semestre_num = patron_periodo.group(2)
                # Normalizar el semestre a I o II
                semestre = 'I' if semestre_num in ['I', '1'] else 'II'
                nombre_periodo = f"{anio}-{semestre}"
                
                # Buscar o crear el periodo
                from datetime import date
                periodo, created = PeriodoAcademico.objects.get_or_create(
                    nombre=nombre_periodo,
                    defaults={
                        'tipo': 'SEMESTRE',
                        'anio': anio,
                        'fecha_inicio': date(anio, 3 if semestre == 'I' else 8, 1),
                        'fecha_fin': date(anio, 7 if semestre == 'I' else 12, 31)
                    }
                )
                if created:
                    print(f"✓ Periodo académico '{periodo.nombre}' creado automáticamente desde Excel")
        
        # Si no se pudo extraer, usar el periodo activo
        if not periodo:
            periodo = PeriodoAcademico.objects.filter(
                fecha_inicio__lte=datetime.now().date(),
                fecha_fin__gte=datetime.now().date()
            ).first()
        
        # Si tampoco hay periodo activo, crear uno por defecto
        if not periodo:
            from datetime import date
            anio_actual = datetime.now().year
            periodo, created = PeriodoAcademico.objects.get_or_create(
                nombre=f"{anio_actual}-1",
                defaults={
                    'tipo': 'SEMESTRE',
                    'anio': anio_actual,
                    'fecha_inicio': date(anio_actual, 3, 1),
                    'fecha_fin': date(anio_actual, 7, 31)
                }
            )
            if created:
                print(f"✓ Periodo académico '{periodo.nombre}' creado automáticamente")
    
    grupos_creados = 0
    horarios_creados = 0
    errores = []
    
    # Procesar cada hoja del Excel
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        
        try:
            # Buscar las columnas de encabezado (comenzando desde fila 3 o 4)
            header_row = None
            for row_idx, row in enumerate(sheet.iter_rows(min_row=3, max_row=10), 3):
                cell_values = [limpiar_texto(cell.value).upper() for cell in row]
                if 'GRUPO' in cell_values or 'ASIGNATURA' in cell_values:
                    header_row = row_idx
                    break
            
            if not header_row:
                errores.append(f"Hoja '{sheet_name}': No se encontró encabezado")
                continue
            
            # Mapear columnas
            headers = {}
            for col_idx, cell in enumerate(sheet[header_row], 1):
                header_text = limpiar_texto(cell.value).upper()
                # Mapeo según el formato de la imagen
                if 'CICLO' in header_text:
                    headers['ciclo'] = col_idx
                elif 'ASIGNATURA' in header_text:
                    headers['asignatura'] = col_idx
                elif header_text in ['GL', 'GRUPO', 'G']:
                    headers['grupo'] = col_idx
                elif header_text in ['T/P/L', 'T', 'TIPO']:
                    headers['tipo'] = col_idx
                elif 'DIA' in header_text or 'DÍA' in header_text:
                    headers['dia'] = col_idx
                elif 'H.INI' in header_text or 'H_INI' in header_text or 'HORA_INI' in header_text or 'INICIO' in header_text:
                    headers['hora_inicio'] = col_idx
                elif 'H.FIN' in header_text or 'H_FIN' in header_text or 'HORA_FIN' in header_text or 'FIN' in header_text:
                    headers['hora_fin'] = col_idx
                elif 'HORARIO' in header_text and 'hora_inicio' not in headers:
                    # Si hay una columna HORARIO y no hay H_INI/H_FIN separadas
                    headers['horario'] = col_idx
                elif 'DOCENTE' in header_text:
                    headers['docente'] = col_idx
                elif 'AULA' in header_text:
                    headers['aula'] = col_idx
                elif header_text == 'SI':
                    headers['vacantes_si'] = col_idx
                elif header_text == 'SW':
                    headers['vacantes_sw'] = col_idx
                elif header_text == 'CC':
                    headers['vacantes_cc'] = col_idx
                elif header_text == 'TOTAL' and 'vacantes' not in headers:
                    headers['vacantes_total'] = col_idx
            
            # Procesar filas de datos
            for row_idx in range(header_row + 1, sheet.max_row + 1):
                row = sheet[row_idx]
                
                # Extraer datos de la fila
                nombre_asignatura = limpiar_texto(row[headers.get('asignatura', 1) - 1].value) if 'asignatura' in headers else None
                nombre_grupo = limpiar_texto(row[headers.get('grupo', 2) - 1].value) if 'grupo' in headers else None
                tipo_sesion = limpiar_texto(row[headers.get('tipo', 3) - 1].value) if 'tipo' in headers else 'T'
                dia_texto = limpiar_texto(row[headers.get('dia', 4) - 1].value) if 'dia' in headers else None
                nombre_docente = limpiar_texto(row[headers.get('docente', 8) - 1].value) if 'docente' in headers else None
                nombre_aula = limpiar_texto(row[headers.get('aula', 9) - 1].value) if 'aula' in headers else None
                
                # Procesar horario (puede estar en columnas separadas o combinado)
                hora_inicio = None
                hora_fin = None
                
                if 'hora_inicio' in headers and 'hora_fin' in headers:
                    # Horas en columnas separadas
                    hora_inicio_texto = row[headers['hora_inicio'] - 1].value
                    hora_fin_texto = row[headers['hora_fin'] - 1].value
                    hora_inicio = interpretar_hora(hora_inicio_texto)
                    hora_fin = interpretar_hora(hora_fin_texto)
                elif 'horario' in headers:
                    # Horario combinado (formato "08:00 10:00" o "08:00 - 10:00")
                    horario_texto = limpiar_texto(row[headers['horario'] - 1].value)
                    if horario_texto:
                        horario_partes = re.split(r'[-\s]+', horario_texto)
                        if len(horario_partes) >= 2:
                            hora_inicio = interpretar_hora(horario_partes[0])
                            hora_fin = interpretar_hora(horario_partes[1])
                
                # Validar datos mínimos
                if not nombre_grupo or not nombre_asignatura:
                    continue
                
                # Buscar asignatura
                try:
                    asignatura = Asignatura.objects.filter(nombre__icontains=nombre_asignatura).first()
                    if not asignatura:
                        # Intentar buscar por palabras clave
                        palabras = nombre_asignatura.split()
                        if len(palabras) >= 2:
                            asignatura = Asignatura.objects.filter(nombre__icontains=palabras[0]).first()
                    
                    if not asignatura:
                        errores.append(f"Fila {row_idx}: Asignatura '{nombre_asignatura}' no encontrada")
                        continue
                except Exception as e:
                    errores.append(f"Fila {row_idx}: Error buscando asignatura - {str(e)}")
                    continue
                
                # Obtener o crear grupo
                docente = obtener_o_crear_docente(nombre_docente) if nombre_docente else None
                
                grupo, grupo_creado = Grupo.objects.get_or_create(
                    nombre=nombre_grupo,
                    asignatura=asignatura,
                    periodo=periodo,
                    defaults={'docente': docente}
                )
                
                if grupo_creado:
                    grupos_creados += 1
                
                # Procesar distribución de vacantes desde el Excel
                vacantes_info = {}
                if 'vacantes_si' in headers:
                    val_si = row[headers['vacantes_si'] - 1].value
                    if val_si and str(val_si).strip() and str(val_si).strip() != '0':
                        try:
                            vacantes_info['SI'] = int(float(val_si))
                        except (ValueError, TypeError):
                            pass
                
                if 'vacantes_sw' in headers:
                    val_sw = row[headers['vacantes_sw'] - 1].value
                    if val_sw and str(val_sw).strip() and str(val_sw).strip() != '0':
                        try:
                            vacantes_info['SW'] = int(float(val_sw))
                        except (ValueError, TypeError):
                            pass
                
                if 'vacantes_cc' in headers:
                    val_cc = row[headers['vacantes_cc'] - 1].value
                    if val_cc and str(val_cc).strip() and str(val_cc).strip() != '0':
                        try:
                            vacantes_info['CC'] = int(float(val_cc))
                        except (ValueError, TypeError):
                            pass
                
                # Crear distribuciones de vacantes por escuela
                if vacantes_info:
                    for escuela_codigo, cantidad in vacantes_info.items():
                        if cantidad > 0:
                            DistribucionVacantes.objects.get_or_create(
                                grupo=grupo,
                                asignatura=asignatura,
                                defaults={'cantidad': cantidad}
                            )
                elif grupo_creado:
                    # Si no hay información de vacantes y es un grupo nuevo, crear vacantes por defecto
                    DistribucionVacantes.objects.get_or_create(
                        grupo=grupo,
                        asignatura=asignatura,
                        defaults={'cantidad': 30}
                    )
                
                # Procesar horario si está disponible
                if dia_texto and hora_inicio and hora_fin:
                    dia_num = interpretar_dia(dia_texto)
                    
                    if dia_num:
                        # Crear o usar aula
                        if nombre_aula:
                            aula = obtener_o_crear_aula(
                                nombre_aula,
                                es_laboratorio=(interpretar_tipo_sesion(tipo_sesion) == 'L')
                            )
                        else:
                            aula = obtener_o_crear_aula(
                                f"AULA-{nombre_grupo}",
                                es_laboratorio=(interpretar_tipo_sesion(tipo_sesion) == 'L')
                            )
                        
                        # Crear horario
                        try:
                            horario, horario_creado = Horario.objects.get_or_create(
                                grupo=grupo,
                                dia=dia_num,
                                hora_inicio=hora_inicio,
                                hora_fin=hora_fin,
                                defaults={
                                    'tipo': interpretar_tipo_sesion(tipo_sesion),
                                    'aula': aula
                                }
                            )
                            
                            if horario_creado:
                                horarios_creados += 1
                        except Exception as e:
                            errores.append(f"Fila {row_idx}: Error creando horario - {str(e)}")
        
        except Exception as e:
            errores.append(f"Hoja '{sheet_name}': Error general - {str(e)}")
    
    return {
        'success': len(errores) == 0 or (grupos_creados > 0 or horarios_creados > 0),
        'grupos_creados': grupos_creados,
        'horarios_creados': horarios_creados,
        'errores': errores,
        'periodo': str(periodo)
    }
