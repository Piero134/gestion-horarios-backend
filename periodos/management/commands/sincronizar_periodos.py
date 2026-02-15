from django.core.management.base import BaseCommand
from periodos.models import PeriodoAcademico
from periodos.services import UnmsmScraperService
from django.db import transaction

class Command(BaseCommand):
    help = 'Extrae cronograma oficial de la web del SUM UNMSM'

    def handle(self, *args, **options):
        self.stdout.write("📡 Conectando al SUM UNMSM...")

        datos = UnmsmScraperService.obtener_periodos()

        if not datos:
            self.stdout.write(self.style.WARNING("No se encontraron datos o hubo error de conexión."))
            return

        count_created = 0
        count_updated = 0

        for item in datos:
            # Usamos update_or_create para no duplicar si corres el script varias veces
            obj, created = PeriodoAcademico.objects.update_or_create(
                nombre=item['nombre'],
                defaults={
                    'tipo': item['tipo'],
                    'anio': item['anio'],
                    'fecha_inicio': item['fecha_inicio'],
                    'fecha_fin': item['fecha_fin'],
                    'fuente': item['fuente_oficial']
                }
            )

            if created:
                count_created += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Creado: {obj} ({obj.fecha_inicio} - {obj.fecha_fin})"))
            else:
                count_updated += 1
                self.stdout.write(self.style.WARNING(f"🔄 Actualizado: {obj}"))

        self.stdout.write(self.style.SUCCESS(f"\nResumen: {count_created} nuevos, {count_updated} actualizados."))
