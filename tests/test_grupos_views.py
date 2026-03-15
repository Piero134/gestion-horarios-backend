from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from grupos.models import Grupo
from periodos.models import PeriodoAcademico

from .utils import BaseDataMixin


class GruposViewsTests(BaseDataMixin, TestCase):
    def test_list_defaults_to_allowed_school_and_active_period(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("grupos_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["filtros"]["escuela"], str(self.escuela.id))
        self.assertEqual(response.context["filtros"]["periodo"], self.periodo_activo.id)
        self.assertIn(self.grupo, list(response.context["grupos"]))

    def test_list_limits_cycles_for_coordinator(self):
        self.client.force_login(self.coordinador)

        response = self.client.get(reverse("grupos_list"))

        self.assertEqual(list(response.context["ciclos"]), [1, 2])
        self.assertIn(self.grupo_eg, list(response.context["grupos"]))
        self.assertNotIn(self.grupo, list(response.context["grupos"]))

    def test_detail_returns_404_for_group_outside_user_scope(self):
        grupo_externo = Grupo.objects.create(
            numero=8,
            asignatura=self.asignatura_externa,
            periodo=self.periodo_activo,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("grupo_detail", kwargs={"pk": grupo_externo.pk}))

        self.assertEqual(response.status_code, 404)

    def test_create_redirects_when_no_active_period_exists(self):
        PeriodoAcademico.objects.all().delete()
        self.client.force_login(self.user)

        response = self.client.get(reverse("grupo_create"))

        self.assertRedirects(response, reverse("grupos_list"))
        mensajes = [message.message for message in get_messages(response.wsgi_request)]
        self.assertTrue(any("No existe un periodo académico activo" in mensaje for mensaje in mensajes))

    def test_delete_removes_group_in_scope(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("grupo_delete", kwargs={"pk": self.grupo.pk}))

        self.assertRedirects(response, reverse("grupos_list"))
        self.assertFalse(Grupo.objects.filter(pk=self.grupo.pk).exists())

    def test_create_persists_group_with_horarios_and_vacantes(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("grupo_create"),
            {
                "numero": "9",
                "asignatura": str(self.asignatura.id),
                "horarios-TOTAL_FORMS": "2",
                "horarios-INITIAL_FORMS": "0",
                "horarios-MIN_NUM_FORMS": "0",
                "horarios-MAX_NUM_FORMS": "1000",
                "horarios-0-dia": "1",
                "horarios-0-hora_inicio": "10:00",
                "horarios-0-hora_fin": "12:00",
                "horarios-0-tipo": "T",
                "horarios-0-aula": "",
                "horarios-0-docente": "",
                "horarios-1-dia": "2",
                "horarios-1-hora_inicio": "14:00",
                "horarios-1-hora_fin": "16:00",
                "horarios-1-tipo": "P",
                "horarios-1-aula": "",
                "horarios-1-docente": "",
                "vacantes-TOTAL_FORMS": "1",
                "vacantes-INITIAL_FORMS": "0",
                "vacantes-MIN_NUM_FORMS": "0",
                "vacantes-MAX_NUM_FORMS": "1000",
                "vacantes-0-asignatura": str(self.asignatura.id),
                "vacantes-0-cantidad": "25",
            },
        )

        grupo = Grupo.objects.get(numero=9, asignatura=self.asignatura, periodo=self.periodo_activo)
        self.assertRedirects(response, reverse("grupo_detail", kwargs={"pk": grupo.pk}))
        self.assertEqual(grupo.horarios.count(), 2)
        self.assertEqual(grupo.vacantes.count(), 1)

    def test_edit_updates_group_and_adds_vacantes(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("grupo_edit", kwargs={"pk": self.grupo.pk}),
            {
                "numero": "7",
                "asignatura": str(self.asignatura.id),
                "horarios-TOTAL_FORMS": "2",
                "horarios-INITIAL_FORMS": "1",
                "horarios-MIN_NUM_FORMS": "0",
                "horarios-MAX_NUM_FORMS": "1000",
                "horarios-0-id": str(self.horario.id),
                "horarios-0-dia": "1",
                "horarios-0-hora_inicio": "08:00",
                "horarios-0-hora_fin": "10:00",
                "horarios-0-tipo": "T",
                "horarios-0-aula": str(self.aula.id),
                "horarios-0-docente": str(self.docente.id),
                "horarios-0-grupo": str(self.grupo.id),
                "horarios-1-id": "",
                "horarios-1-dia": "2",
                "horarios-1-hora_inicio": "10:00",
                "horarios-1-hora_fin": "12:00",
                "horarios-1-tipo": "P",
                "horarios-1-aula": "",
                "horarios-1-docente": "",
                "horarios-1-grupo": str(self.grupo.id),
                "vacantes-TOTAL_FORMS": "1",
                "vacantes-INITIAL_FORMS": "0",
                "vacantes-MIN_NUM_FORMS": "0",
                "vacantes-MAX_NUM_FORMS": "1000",
                "vacantes-0-id": "",
                "vacantes-0-asignatura": str(self.asignatura.id),
                "vacantes-0-cantidad": "30",
                "vacantes-0-grupo": str(self.grupo.id),
            },
        )

        self.assertRedirects(response, reverse("grupo_detail", kwargs={"pk": self.grupo.pk}))
        self.grupo.refresh_from_db()
        self.assertEqual(self.grupo.numero, 7)
        self.assertEqual(self.grupo.horarios.count(), 2)
        self.assertEqual(self.grupo.vacantes.count(), 1)
