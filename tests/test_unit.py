from datetime import date, timedelta, time

from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import Usuario
from escuelas.models import Escuela
from horarios.models import Horario
from periodos.models import PeriodoAcademico

from .utils import BaseDataMixin


class UsuarioModelTests(BaseDataMixin, TestCase):
    def test_secretaria_role_requires_school(self):
        user = Usuario(
            email="sin-escuela@example.com",
            rol=self.rol_secretaria,
            facultad=self.facultad,
        )
        user.set_password(self.password)

        with self.assertRaises(ValidationError) as error:
            user.full_clean()

        self.assertIn("escuela", error.exception.message_dict)


class PeriodoAcademicoModelTests(BaseDataMixin, TestCase):
    def test_get_activo_returns_current_period(self):
        activo = PeriodoAcademico.objects.get_activo()

        self.assertEqual(activo, self.periodo_activo)
        self.assertTrue(activo.activo)

    def test_clean_rejects_overlapping_periods(self):
        periodo = PeriodoAcademico(
            nombre="2026-II",
            tipo="SEMESTRE",
            anio=2026,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=30),
        )

        with self.assertRaises(ValidationError):
            periodo.full_clean()


class EscuelaQuerySetTests(BaseDataMixin, TestCase):
    def test_para_usuario_limits_secretaria_to_own_school(self):
        escuelas = list(Escuela.objects.para_usuario(self.user))

        self.assertEqual(escuelas, [self.escuela])

    def test_para_usuario_limits_coordinador_to_primary_school(self):
        escuelas = list(Escuela.objects.para_usuario(self.coordinador))

        self.assertEqual(escuelas, [self.escuela])


class HorarioModelTests(BaseDataMixin, TestCase):
    def test_clean_rejects_teacher_overlap(self):
        otro_grupo = self.grupo.__class__.objects.create(
            numero=5,
            asignatura=self.asignatura,
            periodo=self.periodo_activo,
        )
        horario = Horario(
            grupo=otro_grupo,
            tipo="T",
            dia=1,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            docente=self.docente,
        )

        with self.assertRaises(ValidationError) as error:
            horario.full_clean()

        self.assertIn("docente", error.exception.message_dict)

    def test_clean_rejects_hours_above_subject_limit(self):
        horario = Horario(
            grupo=self.grupo,
            tipo="T",
            dia=2,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
        )

        with self.assertRaises(ValidationError) as error:
            horario.full_clean()

        self.assertIn("exceden lo permitido", str(error.exception))
