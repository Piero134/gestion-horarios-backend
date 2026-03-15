from datetime import date, timedelta, time

from django.core.exceptions import ValidationError
from django.test import TestCase

from asignaturas.models import Prerequisito
from aulas.models import Aula
from docentes.models import Docente
from grupos.models import DistribucionVacantes, Grupo
from horarios.models import Horario
from periodos.models import PeriodoAcademico

from .utils import BaseDataMixin


class PrerequisitoModelTests(BaseDataMixin, TestCase):
    def test_rejects_self_as_prerequisite(self):
        prerequisito = Prerequisito(
            asignatura=self.asignatura,
            prerequisito=self.asignatura,
        )

        with self.assertRaises(ValidationError):
            prerequisito.full_clean()

    def test_rejects_prerequisite_from_same_or_higher_cycle(self):
        prerequisito = Prerequisito(
            asignatura=self.asignatura,
            prerequisito=self.asignatura_otra_escuela,
        )

        with self.assertRaises(ValidationError):
            prerequisito.full_clean()


class DistribucionVacantesModelTests(BaseDataMixin, TestCase):
    def test_accepts_base_subject_as_vacancy_distribution(self):
        vacante = DistribucionVacantes.objects.create(
            grupo=self.grupo,
            asignatura=self.asignatura,
            cantidad=20,
        )

        self.assertEqual(vacante.cantidad, 20)

    def test_rejects_non_equivalent_subject(self):
        vacante = DistribucionVacantes(
            grupo=self.grupo,
            asignatura=self.asignatura_externa,
            cantidad=10,
        )

        with self.assertRaises(ValidationError):
            vacante.full_clean()


class GrupoModelTests(BaseDataMixin, TestCase):
    def test_total_vacantes_sums_all_distributions(self):
        DistribucionVacantes.objects.create(grupo=self.grupo, asignatura=self.asignatura, cantidad=20)
        DistribucionVacantes.objects.create(grupo=self.grupo, asignatura=self.asignatura_otra_escuela, cantidad=5)

        self.assertEqual(self.grupo.total_vacantes, 25)

    def test_validar_horarios_detects_incomplete_load(self):
        with self.assertRaises(ValidationError) as error:
            self.grupo.validar_horarios()

        self.assertIn("carga horaria", str(error.exception))

    def test_actuales_de_docente_y_buscar_querysets(self):
        self.assertIn(self.grupo, list(Grupo.objects.actuales()))
        self.assertIn(self.grupo, list(Grupo.objects.de_docente(self.docente.id)))
        self.assertIn(self.grupo, list(Grupo.objects.buscar("PEREZ")))


class DocenteModelTests(BaseDataMixin, TestCase):
    def test_nombrado_requires_department_code_category_and_dedication(self):
        docente = Docente(
            apellido_paterno="LOPEZ",
            apellido_materno="RAMOS",
            nombres="ELSA",
            dni="22334455",
            tipo=Docente.TipoDocente.NOMBRADO,
            facultad=self.facultad,
        )

        with self.assertRaises(ValidationError) as error:
            docente.full_clean()

        self.assertIn("departamento", error.exception.message_dict)
        self.assertIn("codigo", error.exception.message_dict)

    def test_contratado_clears_named_only_fields(self):
        docente = Docente(
            apellido_paterno="LOPEZ",
            apellido_materno="RAMOS",
            nombres="ELSA",
            dni="22334456",
            tipo=Docente.TipoDocente.CONTRATADO,
            facultad=self.facultad,
            departamento=self.departamento,
            codigo="DOC-999",
            categoria=Docente.Categoria.AUXILIAR,
            dedicacion=Docente.Dedicacion.TIEMPO_COMPLETO,
        )

        docente.full_clean()

        self.assertIsNone(docente.departamento)
        self.assertIsNone(docente.codigo)
        self.assertIsNone(docente.categoria)
        self.assertIsNone(docente.dedicacion)

    def test_rejects_department_from_other_faculty(self):
        otro_departamento = self.departamento.__class__.objects.create(
            nombre="Gestion",
            facultad=self.otra_facultad,
        )
        docente = Docente(
            apellido_paterno="SUAREZ",
            apellido_materno="TORRES",
            nombres="NORA",
            dni="22334457",
            tipo=Docente.TipoDocente.NOMBRADO,
            facultad=self.facultad,
            departamento=otro_departamento,
            codigo="DOC-100",
            categoria=Docente.Categoria.AUXILIAR,
            dedicacion=Docente.Dedicacion.TIEMPO_COMPLETO,
        )

        with self.assertRaises(ValidationError):
            docente.full_clean()

    def test_activar_y_desactivar_toggle_state(self):
        self.docente.desactivar()
        self.docente.refresh_from_db()
        self.assertFalse(self.docente.activo)

        self.docente.activar()
        self.docente.refresh_from_db()
        self.assertTrue(self.docente.activo)


class AulaModelTests(BaseDataMixin, TestCase):
    def test_type_properties_reflect_room_kind(self):
        self.assertTrue(self.aula.es_aula)
        self.assertFalse(self.aula.es_laboratorio)

        laboratorio = Aula.objects.create(
            nombre="LAB1",
            pabellon=Aula.Pabellon.NUEVO_PABELLON,
            vacantes=25,
            tipo=Aula.Tipo.LABORATORIO,
            facultad=self.facultad,
        )

        self.assertFalse(laboratorio.es_aula)
        self.assertTrue(laboratorio.es_laboratorio)
