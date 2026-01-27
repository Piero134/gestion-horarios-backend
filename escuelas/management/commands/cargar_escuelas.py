import csv
from django.core.management.base import BaseCommand
from facultades.models import Facultad
from escuelas.models import Escuela


class Command(BaseCommand):
    help = "Carga las Escuelas Académico-Profesionales desde un archivo CSV"

    def handle(self, *args, **options):
        ruta_csv = 'escuelas/management/commands/escuelas.csv'

        with open(ruta_csv, newline='', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo)

            contador_por_facultad = {}

            for fila in lector:
                nombre_facultad = fila['facultad'].strip()
                nombre_escuela = fila['escuela'].strip()

                facultad = Facultad.objects.get(
                    nombre=nombre_facultad
                )

                if facultad.id not in contador_por_facultad:
                    contador_por_facultad[facultad.id] = (
                        Escuela.objects.filter(facultad=facultad).count()
                    )

                contador_por_facultad[facultad.id] += 1

                codigo = f"{facultad.codigo}.{contador_por_facultad[facultad.id]}"

                Escuela.objects.get_or_create(
                    facultad=facultad,
                    nombre=nombre_escuela,
                    defaults={'codigo': codigo}
                )

        self.stdout.write(
            self.style.SUCCESS('✔ Facultades y escuelas cargadas correctamente')
        )
