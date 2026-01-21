import csv
from django.core.management.base import BaseCommand
from facultades.models import Facultad

class Command(BaseCommand):
    help = "Carga las facultades desde un archivo CSV"


    def handle(self, *args, **options):
        csv_file = 'facultades/management/commands/facultades.csv'

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                facultad, created = Facultad.objects.update_or_create(
                    codigo=row['codigo'],
                    defaults={
                        'nombre': row['nombre'],
                        'siglas': row['siglas']
                    }
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"✔ Facultad creada: {facultad}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"↺ Facultad actualizada: {facultad}")
                    )

        self.stdout.write(self.style.SUCCESS("✔ Carga de facultades finalizada"))
