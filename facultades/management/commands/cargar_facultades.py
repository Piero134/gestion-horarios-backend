import csv
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from facultades.models import Facultad, Departamento
from escuelas.models import Escuela


class Command(BaseCommand):
    help = "Carga Facultades, Escuelas y Departamentos desde CSV"

    def handle(self, *args, **options):
        base_path = os.path.join(settings.BASE_DIR, 'facultades', 'management', 'commands')

        archivos = {
            "facultades": os.path.join(base_path, 'facultades.csv'),
            "escuelas": os.path.join(base_path, 'escuelas.csv'),
            "departamentos": os.path.join(base_path, 'departamentos.csv'),
        }

        try:
            with transaction.atomic():
                self.stdout.write("=== INICIANDO CARGA ===")

                if os.path.exists(archivos["facultades"]):
                    self.cargar_facultades(archivos["facultades"])

                if os.path.exists(archivos["escuelas"]):
                    self.cargar_escuelas(archivos["escuelas"])

                if os.path.exists(archivos["departamentos"]):
                    self.cargar_departamentos(archivos["departamentos"])

                self.stdout.write(self.style.SUCCESS("=== CARGA COMPLETADA ==="))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error durante la carga: {e}"))

    def cargar_facultades(self, ruta):
        with open(ruta, newline='', encoding='utf-8') as file:
            for row in csv.DictReader(file):
                Facultad.objects.update_or_create(
                    codigo=row['codigo'],
                    defaults={
                        'nombre': row['nombre'],
                        'siglas': row['siglas']
                    }
                )

    def cargar_escuelas(self, ruta):
        with open(ruta, newline='', encoding='utf-8') as file:
            for row in csv.DictReader(file):
                try:
                    facultad = Facultad.objects.get(nombre=row['facultad'].strip())
                except Facultad.DoesNotExist:
                    continue

                nombre = row['escuela'].strip()

                if not Escuela.objects.filter(facultad=facultad, nombre=nombre).exists():
                    numero = Escuela.objects.filter(facultad=facultad).count() + 1
                    Escuela.objects.create(
                        facultad=facultad,
                        nombre=nombre,
                        codigo=f"{facultad.codigo}.{numero}"
                    )

    def cargar_departamentos(self, ruta):
        with open(ruta, newline='', encoding='utf-8') as file:
            for row in csv.DictReader(file):
                try:
                    facultad = Facultad.objects.get(codigo=row['facultad_codigo'])
                    Departamento.objects.get_or_create(
                        facultad=facultad,
                        nombre=row['nombre']
                    )
                except Facultad.DoesNotExist:
                    continue
