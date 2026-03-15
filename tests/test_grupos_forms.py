from datetime import time

from django.forms import inlineformset_factory
from django.test import TestCase

from grupos.forms import (
    DistribucionVacantesForm,
    DistribucionVacantesFormSet,
    GrupoForm,
    HorarioForm,
    HorarioFormSet,
)
from grupos.models import DistribucionVacantes

from .utils import BaseDataMixin


class GrupoFormTests(BaseDataMixin, TestCase):
    def test_limits_school_filter_for_secretaria(self):
        form = GrupoForm(user=self.user, periodo_activo=self.periodo_activo)

        self.assertEqual(list(form.fields["escuela_filtro"].queryset), [self.escuela])
        self.assertTrue(form.fields["escuela_filtro"].disabled)

    def test_allows_vicedecano_to_see_all_schools_in_faculty(self):
        form = GrupoForm(user=self.vicedecano, periodo_activo=self.periodo_activo)

        self.assertEqual(
            list(form.fields["escuela_filtro"].queryset),
            [self.escuela, self.otra_escuela],
        )
        self.assertFalse(form.fields["escuela_filtro"].disabled)

    def test_rejects_duplicate_group_number_in_active_period(self):
        form = GrupoForm(
            data={"numero": self.grupo.numero, "asignatura": self.asignatura.id},
            user=self.user,
            periodo_activo=self.periodo_activo,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("Ya existe un grupo", form.errors["numero"][0])


class HorarioFormTests(BaseDataMixin, TestCase):
    def test_limits_aula_and_docente_queryset_to_user_faculty(self):
        form = HorarioForm(user=self.user)

        self.assertEqual(list(form.fields["aula"].queryset), [self.aula])
        self.assertEqual(list(form.fields["docente"].queryset), [self.docente])

    def test_rejects_teacher_collision_for_same_period(self):
        otro_grupo = self.grupo.__class__.objects.create(
            numero=4,
            asignatura=self.asignatura,
            periodo=self.periodo_activo,
        )
        form = HorarioForm(
            data={
                "dia": 1,
                "hora_inicio": "09:00",
                "hora_fin": "10:00",
                "tipo": "T",
                "aula": self.aula.id,
                "docente": self.docente.id,
            },
            initial={"grupo": otro_grupo},
            user=self.user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("docente", form.errors)


class HorarioFormSetTests(BaseDataMixin, TestCase):
    def test_rejects_when_no_schedule_is_submitted(self):
        formset = HorarioFormSet(
            data={
                "horarios-TOTAL_FORMS": "1",
                "horarios-INITIAL_FORMS": "0",
                "horarios-MIN_NUM_FORMS": "0",
                "horarios-MAX_NUM_FORMS": "1000",
                "horarios-0-dia": "",
                "horarios-0-hora_inicio": "",
                "horarios-0-hora_fin": "",
                "horarios-0-tipo": "",
                "horarios-0-aula": "",
                "horarios-0-docente": "",
            },
            instance=self.grupo,
            prefix="horarios",
        )

        self.assertFalse(formset.is_valid())
        self.assertIn("Debe registrar al menos un horario.", formset.non_form_errors())

    def test_rejects_overlapping_schedules_within_same_submission(self):
        formset = HorarioFormSet(
            data={
                "horarios-TOTAL_FORMS": "2",
                "horarios-INITIAL_FORMS": "0",
                "horarios-MIN_NUM_FORMS": "0",
                "horarios-MAX_NUM_FORMS": "1000",
                "horarios-0-dia": "1",
                "horarios-0-hora_inicio": "08:00",
                "horarios-0-hora_fin": "09:00",
                "horarios-0-tipo": "T",
                "horarios-0-aula": self.aula.id,
                "horarios-0-docente": self.docente.id,
                "horarios-1-dia": "1",
                "horarios-1-hora_inicio": "08:30",
                "horarios-1-hora_fin": "09:30",
                "horarios-1-tipo": "T",
                "horarios-1-aula": "",
                "horarios-1-docente": "",
            },
            instance=self.grupo_eg,
            prefix="horarios",
        )

        self.assertFalse(formset.is_valid())
        errores = " ".join(formset.forms[0].non_field_errors())
        self.assertIn("cruza con", errores)


class DistribucionVacantesFormTests(BaseDataMixin, TestCase):
    def test_limits_assignments_for_secretaria_to_own_school(self):
        form = DistribucionVacantesForm(user=self.user)

        self.assertEqual(form.fields["asignatura"].queryset.count(), 0)

        bound_form = DistribucionVacantesForm(
            data={"asignatura": self.asignatura_otra_escuela.id, "cantidad": 10},
            prefix="vacantes-0",
            user=self.user,
        )

        self.assertEqual(list(bound_form.fields["asignatura"].queryset), [])


class DistribucionVacantesFormSetTests(BaseDataMixin, TestCase):
    def test_rejects_duplicate_subjects(self):
        formset = DistribucionVacantesFormSet(
            data={
                "vacantes-TOTAL_FORMS": "2",
                "vacantes-INITIAL_FORMS": "0",
                "vacantes-MIN_NUM_FORMS": "0",
                "vacantes-MAX_NUM_FORMS": "1000",
                "vacantes-0-asignatura": str(self.asignatura.id),
                "vacantes-0-cantidad": "10",
                "vacantes-1-asignatura": str(self.asignatura.id),
                "vacantes-1-cantidad": "5",
            },
            instance=self.grupo,
            prefix="vacantes",
            user=self.user,
        )

        self.assertFalse(formset.is_valid())
        self.assertIn("duplicate", formset.non_form_errors()[0].lower())
