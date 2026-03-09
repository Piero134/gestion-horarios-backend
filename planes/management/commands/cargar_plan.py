import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
from django.core.exceptions import ValidationError

from escuelas.models import Escuela
from planes.models import PlanEstudios
from asignaturas.models import Asignatura, Prerequisito

class Command(BaseCommand):
    help = 'Carga masiva de planes respetando validaciones de Prerrequisitos y Escuela'

    def safe_int(self, valor):
        if not valor: return 0
        try:
            return int(float(valor))
        except (ValueError, TypeError):
            return 0

    def handle(self, *args, **kwargs):
        DATA_DIR = os.path.join(settings.BASE_DIR, 'planes', 'data')

        self.stdout.write(f"--- Iniciando carga desde: {DATA_DIR} ---")

        if not os.path.exists(DATA_DIR):
            raise CommandError(f"La carpeta {DATA_DIR} no existe.")

        archivos = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]

        if not archivos:
            self.stdout.write(self.style.WARNING("No se encontraron archivos CSV."))
            return

        for archivo in archivos:
            ruta = os.path.join(DATA_DIR, archivo)
            try:
                # Transacción: Si falla algo en un archivo, se revierte todo ese archivo
                with transaction.atomic():
                    self.procesar_archivo(ruta)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fatal en '{archivo}': {str(e)}"))

        self.stdout.write(self.style.SUCCESS('\n=== PROCESO COMPLETADO ==='))

    def procesar_archivo(self, ruta):
        with open(ruta, encoding='utf-8') as f:
            try:
                linea_1 = f.readline()
                linea_2 = f.readline()

                nombre_escuela = linea_1.split(';')[1].strip()
                anio_plan = linea_2.split(';')[1].replace('Plan', '').strip()
            except IndexError:
                raise CommandError("Formato de cabecera inválido (Filas 1 y 2).")

            self.stdout.write(f"\n--> Procesando: {nombre_escuela} | {anio_plan}")

            try:
                escuela_obj = Escuela.objects.get(nombre__iexact=nombre_escuela)
            except Escuela.DoesNotExist:
                raise CommandError(f"La escuela '{nombre_escuela}' no existe en la Base de Datos.")

            plan_obj, _ = PlanEstudios.objects.get_or_create(
                anio=anio_plan,
                escuela=escuela_obj
            )

            reader = csv.DictReader(f, delimiter=';')

            # Memoria para prerrequisitos: lista de tuplas (codigo_asignatura, codigo_requisito)
            lista_relaciones = []
            count_cursos = 0

            for row in reader:
                codigo = row.get('Codigo')
                if not codigo: continue

                ciclo = self.safe_int(row.get('Ciclo'))
                creditos = self.safe_int(row.get('Creditos'))
                tipo_raw = row.get('Tipo', 'O').strip()

                Asignatura.objects.update_or_create(
                    codigo=codigo,
                    plan=plan_obj,
                    defaults={
                        'nombre': row.get('Nombre', 'SIN NOMBRE'),
                        'ciclo': ciclo,
                        'creditos': creditos,
                        'tipo': tipo_raw,
                        'horas_teoria': self.safe_int(row.get('HT')),
                        'horas_practica': self.safe_int(row.get('HP')),
                        'horas_laboratorio': self.safe_int(row.get('HL')),
                    }
                )
                count_cursos += 1

                # Manejo de prerrequisitos
                req_raw = row.get('Prerequisito')
                if req_raw and req_raw.strip():
                    req_code = req_raw.strip().split('-')[0].strip()
                    lista_relaciones.append((codigo, req_code))

            self.stdout.write(f"    ✔ Asignaturas procesadas: {count_cursos}")

            qs_asignaturas = Asignatura.objects.filter(plan=plan_obj)

            mapa_asignaturas = {asig.codigo: asig for asig in qs_asignaturas}

            ids_asignaturas_plan = [asig.id for asig in mapa_asignaturas.values()]

            # borramos los prerrequisitos previos de estas asignaturas
            deleted_count, _ = Prerequisito.objects.filter(asignatura_id__in=ids_asignaturas_plan).delete()

            if deleted_count > 0:
                self.stdout.write(f"    Combinando relaciones previas... (Se eliminaron {deleted_count} antiguas)")

            # crear las nuevas relaciones de prerrequisitos
            count_rels = 0
            errores_validacion = 0

            for cod_asig, cod_req in lista_relaciones:
                asig_obj = mapa_asignaturas.get(cod_asig)
                req_obj = mapa_asignaturas.get(cod_req)

                if asig_obj and req_obj:
                    try:
                        Prerequisito.objects.create(
                            asignatura=asig_obj,
                            prerequisito=req_obj
                        )
                        count_rels += 1

                    except ValidationError as e:
                        self.stdout.write(self.style.WARNING(f"    [!] Error validación ({cod_asig} <- {cod_req}): {e.messages[0]}"))
                        errores_validacion += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"    [!] Error desconocido creando relación: {e}"))
                else:
                    falta = []
                    if not asig_obj: falta.append(f"Curso {cod_asig}")
                    if not req_obj: falta.append(f"Requisito {cod_req}")
                    texto_falta = " y ".join(falta)
                    self.stdout.write(self.style.WARNING(f"    [!] No encontrado en BD: {texto_falta}"))

            msg = f"    ✔ Relaciones creadas: {count_rels}"
            if errores_validacion > 0:
                msg += f" (Omitidas por lógica de ciclo: {errores_validacion})"

            self.stdout.write(self.style.SUCCESS(msg))
