import os
import tempfile
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings

from asignaturas.models import Asignatura, Prerequisito
from escuelas.models import Escuela
from facultades.models import Departamento, Facultad
from periodos.models import PeriodoAcademico
from planes.models import PlanEstudios

from .utils import BaseDataMixin


class SincronizarPeriodosCommandTests(BaseDataMixin, TestCase):
    @patch("periodos.management.commands.sincronizar_periodos.UnmsmScraperService.obtener_periodos")
    def test_creates_and_updates_periods_from_scraper(self, mocked_obtener_periodos):
        PeriodoAcademico.objects.create(
            nombre="2026-II",
            tipo="SEMESTRE",
            anio=2026,
            fecha_inicio=self.periodo_activo.fecha_fin,
            fecha_fin=self.periodo_activo.fecha_fin,
        )
        mocked_obtener_periodos.return_value = [
            {
                "nombre": "2026-I",
                "tipo": "SEMESTRE",
                "anio": 2026,
                "fecha_inicio": self.periodo_activo.fecha_inicio,
                "fecha_fin": self.periodo_activo.fecha_fin,
                "fuente_oficial": "https://example.com/2026-1",
            },
            {
                "nombre": "2027-0",
                "tipo": "VERANO",
                "anio": 2027,
                "fecha_inicio": self.periodo_activo.fecha_fin,
                "fecha_fin": self.periodo_activo.fecha_fin,
                "fuente_oficial": "https://example.com/2027-0",
            },
        ]

        out = StringIO()
        call_command("sincronizar_periodos", stdout=out)

        self.assertTrue(PeriodoAcademico.objects.filter(nombre="2026-I", fuente="https://example.com/2026-1").exists())
        self.assertTrue(PeriodoAcademico.objects.filter(nombre="2027-0").exists())
        self.assertIn("Resumen:", out.getvalue())

    @patch("periodos.management.commands.sincronizar_periodos.UnmsmScraperService.obtener_periodos", return_value=[])
    def test_handles_empty_scraper_response(self, _mocked):
        out = StringIO()

        call_command("sincronizar_periodos", stdout=out)

        self.assertIn("No se encontraron datos", out.getvalue())


class CargarFacultadesCommandTests(TestCase):
    @override_settings(BASE_DIR="/tmp/placeholder")
    def test_loads_faculties_schools_and_departments_from_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = os.path.join(tmpdir, "facultades", "management", "commands")
            os.makedirs(commands_dir)

            with open(os.path.join(commands_dir, "facultades.csv"), "w", encoding="utf-8") as fh:
                fh.write("codigo,nombre,siglas\n10,Ingenieria de Sistemas,FISI\n")
            with open(os.path.join(commands_dir, "escuelas.csv"), "w", encoding="utf-8") as fh:
                fh.write("facultad,escuela\nIngenieria de Sistemas,Ingenieria de Sistemas\n")
            with open(os.path.join(commands_dir, "departamentos.csv"), "w", encoding="utf-8") as fh:
                fh.write("facultad_codigo,nombre\n10,Ciencias de la Computacion\n")

            with override_settings(BASE_DIR=tmpdir):
                out = StringIO()
                call_command("cargar_facultades", stdout=out)

        self.assertTrue(Facultad.objects.filter(nombre="Ingenieria de Sistemas").exists())
        self.assertTrue(Escuela.objects.filter(nombre="Ingenieria de Sistemas").exists())
        self.assertTrue(Departamento.objects.filter(nombre="Ciencias de la Computacion").exists())


class CargarPlanCommandTests(TestCase):
    def test_loads_plan_csv_and_creates_prerequisites(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = os.path.join(tmpdir, "planes", "data")
            os.makedirs(data_dir)

            facultad = Facultad.objects.create(nombre="Ingenieria", siglas="FING", codigo=30)
            escuela = Escuela.objects.create(facultad=facultad, nombre="Ingenieria de Datos")

            csv_path = os.path.join(data_dir, "plan.csv")
            with open(csv_path, "w", encoding="utf-8") as fh:
                fh.write("Escuela;Ingenieria de Datos\n")
                fh.write("Plan;Plan 2025\n")
                fh.write("Codigo;Nombre;Ciclo;Creditos;Tipo;HT;HP;HL;Prerequisito\n")
                fh.write("ID101;Introduccion;1;4;O;2;2;0;\n")
                fh.write("ID201;Estructuras;2;4;O;2;2;0;ID101\n")

            with override_settings(BASE_DIR=tmpdir):
                out = StringIO()
                call_command("cargar_plan", stdout=out)

        plan = PlanEstudios.objects.get(escuela=escuela, anio=2025)
        self.assertTrue(Asignatura.objects.filter(plan=plan, codigo="ID201").exists())
        self.assertTrue(Prerequisito.objects.filter(asignatura__plan=plan).exists())
        self.assertIn("PROCESO COMPLETADO", out.getvalue())
