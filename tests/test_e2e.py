from django.test import TestCase
from django.urls import reverse

from aulas.models import Aula

from .utils import BaseDataMixin


class AulaCreationFlowTests(BaseDataMixin, TestCase):
    def test_user_can_login_create_aula_and_see_it_in_list(self):
        login_response = self.client.post(
            reverse("login"),
            {"username": self.user.email, "password": self.password},
        )

        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(login_response.url, reverse("home"))

        create_response = self.client.post(
            reverse("aula_create"),
            {
                "nombre": "202",
                "pabellon": Aula.Pabellon.NUEVO_PABELLON,
                "vacantes": 35,
                "tipo": Aula.Tipo.AULA,
                "facultad": self.otra_facultad.id,
                "activo": "on",
            },
        )

        self.assertRedirects(create_response, reverse("aula_list"))

        aula = Aula.objects.get(nombre="202", pabellon=Aula.Pabellon.NUEVO_PABELLON)
        self.assertEqual(aula.facultad, self.user.facultad)

        list_response = self.client.get(reverse("aula_list"))

        self.assertContains(list_response, "202")
