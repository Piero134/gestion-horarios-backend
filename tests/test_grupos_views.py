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
