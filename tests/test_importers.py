from io import BytesIO

from django.test import TestCase
from openpyxl import Workbook

from asignaturas.models import Asignatura, Prerequisito
from docentes.models import Docente
from grupos.models import DistribucionVacantes, Grupo
from grupos.utils.importer import (
    ExcelImportError,
    _get_or_create_docente,
    _normalizar_dia,
    _normalizar_tipo,
    _resolver_asignatura_vacante,
    importar_programacion,
)
from planes.models import PlanEstudios
from planes.utils.importer import procesar_excel_plan

from .utils import BaseDataMixin


class GruposImporterHelperTests(BaseDataMixin, TestCase):
    def test_normalizes_day_and_type_values(self):
        self.assertEqual(_normalizar_dia("Miércoles"), "3")
        self.assertEqual(_normalizar_dia("SA"), "6")
        self.assertEqual(_normalizar_tipo("teoria T"), "T")
        self.assertEqual(_normalizar_tipo("laboratorio"), "T")

    def test_resolves_equivalent_subject_for_other_school(self):
        escuela_sw = self.otra_escuela
        escuela_sw.nombre = "Ingeniería de Software"
        escuela_sw.save(update_fields=["nombre"])

        asignatura = _resolver_asignatura_vacante(self.asignatura, "EPISW")

        self.assertEqual(asignatura, self.asignatura_otra_escuela)

    def test_get_or_create_docente_creates_teacher_in_user_faculty(self):
        docente = _get_or_create_docente("RAMOS DIAZ, LUZ", self.user)

        self.assertIsNotNone(docente.pk)
        self.assertEqual(docente.facultad, self.user.facultad)
        self.assertEqual(docente.apellido_paterno, "RAMOS")


class GruposImporterTests(BaseDataMixin, TestCase):
    def build_workbook(self, rows):
        workbook = Workbook()
        sheet = workbook.active
        for row in rows:
            sheet.append(row)
        stream = BytesIO()
        workbook.save(stream)
        stream.seek(0)
        return stream

    def test_importar_programacion_creates_schedule_and_vacancies(self):
        self.escuela.nombre = "Ingeniería de Sistemas"
        self.escuela.save(update_fields=["nombre"])
        archivo = self.build_workbook(
            [
                ["ASIGNATURA", "GRUPO", "DIA", "H.INI", "H.FIN", "DOCENTE", "TIPO", "AULA", "EPSIS"],
                [self.asignatura.nombre, "G3", "Lunes", "10:00", "12:00", "RAMOS DIAZ, LUZ", "T", "101 NP", 15],
            ]
        )

        resultado = importar_programacion(archivo, self.user, self.periodo_activo, self.escuela)

        grupo = Grupo.objects.get(asignatura=self.asignatura, numero=3, periodo=self.periodo_activo)
        self.assertEqual(resultado["creados"], 1)
        self.assertEqual(resultado["errores"], [])
        self.assertEqual(grupo.horarios.count(), 1)
        self.assertEqual(DistribucionVacantes.objects.get(grupo=grupo).cantidad, 15)

    def test_importar_programacion_rejects_missing_header(self):
        archivo = self.build_workbook([["CURSO", "SECCION"], ["X", "1"]])

        with self.assertRaises(ExcelImportError):
            importar_programacion(archivo, self.user, self.periodo_activo, self.escuela)


class PlanesImporterTests(BaseDataMixin, TestCase):
    def build_workbook(self, rows):
        workbook = Workbook()
        sheet = workbook.active
        for row in rows:
            sheet.append(row)
        stream = BytesIO()
        workbook.save(stream)
        stream.seek(0)
        return stream

    def test_procesar_excel_plan_creates_subjects_and_prerequisites(self):
        archivo = self.build_workbook(
            [
                ["CICLO", "TIPO", "CODIGO", "NOMBRE", "CREDITOS", "PREREQUISITO", "HT", "HP", "HL"],
                [1, "O", "CS101", "Introducción", 4, "", 2, 2, 0],
                [2, "O", "CS201", "Estructuras", 4, "CS101", 2, 2, 0],
            ]
        )
        plan = PlanEstudios.objects.create(anio=2024, escuela=self.otra_escuela)

        cursos, relaciones = procesar_excel_plan(plan, archivo)

        self.assertEqual(cursos, 2)
        self.assertEqual(relaciones, 1)
        self.assertTrue(Asignatura.objects.filter(plan=plan, codigo="CS201").exists())
        self.assertTrue(Prerequisito.objects.filter(asignatura__plan=plan).exists())

    def test_procesar_excel_plan_requires_mandatory_columns(self):
        archivo = self.build_workbook([["CODIGO", "NOMBRE"], ["CS101", "Intro"]])

        with self.assertRaises(ValueError):
            procesar_excel_plan(self.plan, archivo)
