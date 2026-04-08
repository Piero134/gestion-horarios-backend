from django.test import TestCase
from django.urls import reverse

from aulas.models import Aula

from .utils import BaseDataMixin


class AulasCrudViewsTests(BaseDataMixin, TestCase):
    def test_create_forces_user_faculty(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("aula_create"),
            {
                "nombre": "303",
                "pabellon": Aula.Pabellon.ANTIGUO_PABELLON,
                "vacantes": 45,
                "tipo": Aula.Tipo.AULA,
                "facultad": self.otra_facultad.id,
                "activo": "on",
            },
        )

        self.assertRedirects(response, reverse("aula_list"))
        aula = Aula.objects.get(nombre="303", pabellon=Aula.Pabellon.ANTIGUO_PABELLON)
        self.assertEqual(aula.facultad, self.facultad)

    def test_update_keeps_user_faculty_even_if_payload_changes_it(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("aula_update", kwargs={"pk": self.aula.pk}),
            {
                "nombre": "101B",
                "pabellon": self.aula.pabellon,
                "vacantes": 60,
                "tipo": self.aula.tipo,
                "facultad": self.otra_facultad.id,
                "activo": "on",
            },
        )

        self.assertRedirects(response, reverse("aula_list"))
        self.aula.refresh_from_db()
        self.assertEqual(self.aula.nombre, "101B")
        self.assertEqual(self.aula.facultad, self.facultad)

    def test_delete_soft_disables_aula(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("aula_delete", kwargs={"pk": self.aula.pk}))

        self.assertRedirects(response, reverse("aula_list"))
        self.aula.refresh_from_db()
        self.assertFalse(self.aula.activo)

    def test_non_superuser_cannot_edit_other_faculty_aula(self):
        aula_externa = Aula.objects.create(
            nombre="401",
            pabellon=Aula.Pabellon.NUEVO_PABELLON,
            vacantes=30,
            tipo=Aula.Tipo.AULA,
            facultad=self.otra_facultad,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("aula_update", kwargs={"pk": aula_externa.pk}))

        self.assertEqual(response.status_code, 404)

    def test_superuser_can_filter_list_by_faculty(self):
        Aula.objects.create(
            nombre="501",
            pabellon=Aula.Pabellon.NUEVO_PABELLON,
            vacantes=50,
            tipo=Aula.Tipo.AULA,
            facultad=self.otra_facultad,
        )
        self.client.force_login(self.superuser)

        response = self.client.get(reverse("aula_list"), {"facultad": self.otra_facultad.id})

        self.assertEqual(response.status_code, 200)
        aulas = list(response.context["aulas"])
        self.assertEqual(len(aulas), 1)
        self.assertEqual(aulas[0].facultad, self.otra_facultad)
