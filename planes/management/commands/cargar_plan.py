import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from escuelas.models import Escuela
from planes.models import PlanEstudios
from asignaturas.models import Asignatura, Prerequisito

class Command(BaseCommand):
    help = "Carga un plan de estudios desde un CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            'archivo_csv',
            type=str,
            help='Nombre del archivo CSV dentro de la carpeta planes_estudio'
        )

    def handle(self, *args, **options):
        archivo = options['archivo_csv']

        ruta_csv = os.path.join(
            settings.BASE_DIR,
            'planes',
            'data',
            archivo
        )

        if not os.path.exists(ruta_csv):
            raise CommandError(f"No se encontró el archivo: {ruta_csv}")

        self.stdout.write(self.style.NOTICE(f"Leyendo archivo: {archivo}"))

        with open(ruta_csv, encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            filas = list(reader)

        try:
            escuela_nombre = filas[0][1].strip()
            plan_nombre = filas[1][1].strip()
        except IndexError:
            raise CommandError("El formato del archivo no es válido (Faltan cabeceras)")


        try:
            with transaction.atomic():
                try:
                    escuela = Escuela.objects.get(nombre__iexact=escuela_nombre)
                except Escuela.DoesNotExist:
                    raise CommandError(f"La escuela '{escuela_nombre}' no existe en la BD.")

                plan, created = PlanEstudios.objects.get_or_create(
                    nombre=plan_nombre,
                    escuela=escuela
                )

                verb = "creado" if created else "seleccionado"
                self.stdout.write(f"Plan {verb}: {plan}")

                asignaturas_por_codigo = {}
                lista_relaciones_prereq = []

                start_index = 3

                for i, fila in enumerate(filas[start_index:], start=start_index+1):

                    if not fila or len(fila) < 2 or not fila[1].strip():
                        continue

                    try:
                        ciclo = int(fila[0])
                        codigo = fila[1].strip()
                        nombre = fila[2].strip()
                        creditos = int(float(fila[3]))
                        tipo = fila[4].strip()
                        prereq_raw = fila[5].strip() if len(fila) > 5 else ''
                    except ValueError as e:
                        self.stdout.write(self.style.WARNING(f"Fila {i} ignorada por error de datos: {e}"))
                        continue

                    asignatura, _ = Asignatura.objects.update_or_create(
                        plan=plan,
                        codigo=codigo,
                        defaults={
                            'nombre': nombre,
                            'ciclo': ciclo,
                            'creditos': creditos,
                            'tipo': tipo
                        }
                    )

                    asignaturas_por_codigo[codigo] = asignatura

                    if prereq_raw:
                        cod_prereq = prereq_raw.split('-')[0].strip()
                        if cod_prereq:
                            lista_relaciones_prereq.append((codigo, cod_prereq))

                ids_asignaturas = [a.id for a in asignaturas_por_codigo.values()]
                Prerequisito.objects.filter(asignatura_id__in=ids_asignaturas).delete()

                count_prereqs = 0
                for cod_asig, cod_req in lista_relaciones_prereq:
                    asig_obj = asignaturas_por_codigo.get(cod_asig)
                    req_obj = asignaturas_por_codigo.get(cod_req)

                    if asig_obj and req_obj:
                        Prerequisito.objects.create(
                            asignatura=asig_obj,
                            prerequisito=req_obj
                        )
                        count_prereqs += 1
                    else:
                        self.stdout.write(self.style.WARNING(
                            f"No se pudo crear relacion: {cod_req} -> {cod_asig} (Alguno no existe)"
                        ))

        except Exception as e:
            raise CommandError(f"Error fatal en la transacción: {e}")

        self.stdout.write(self.style.SUCCESS(f"✔ Proceso finalizado. {len(asignaturas_por_codigo)} asignaturas, {count_prereqs} prerrequisitos."))
