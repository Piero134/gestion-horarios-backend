from django.test import TestCase
from django.urls import reverse

from facultades.models import Departamento

from .utils import BaseDataMixin


class AuxiliaryApiTests(BaseDataMixin, TestCase):
    def test_load_departamentos_returns_department_list(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("api_load_departamentos"),
            {"facultad_id": self.facultad.id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["departamentos"][0]["nombre"], self.departamento.nombre)

    def test_api_escuelas_por_facultad_returns_filtered_schools(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("api_escuelas_por_facultad", kwargs={"facultad_id": self.facultad.id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["escuelas"]), 2)

    def test_cargar_asignaturas_ajax_filters_by_school_and_cycle(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("ajax_cargar_asignaturas"),
            {"escuela_id": self.escuela.id, "ciclo": 1},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["id"], self.asignatura_eg.id)

    def test_asignatura_equivalencias_limits_results_to_user_school(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("api_asignatura_equivalencias"),
            {"id": self.asignatura.id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["equivalencias"], [])
