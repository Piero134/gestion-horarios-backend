from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token

from docentes.models import Docente

from .utils import BaseDataMixin


class AuthTokenApiTests(BaseDataMixin, TestCase):
    def test_returns_token_for_valid_credentials(self):
        response = self.client.post(
            "/api/token/",
            {"email": self.user.email, "password": self.password},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], self.user.email)
        self.assertTrue(Token.objects.filter(user=self.user).exists())

    def test_rejects_invalid_credentials(self):
        response = self.client.post(
            "/api/token/",
            {"email": self.user.email, "password": "incorrecta"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Credenciales inválidas")


class HorarioApiTests(BaseDataMixin, TestCase):
    def test_returns_grouped_schedule_for_authorized_user(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("horarios:api_horarios"),
            {
                "ciclo": self.asignatura.ciclo,
                "grupo": self.grupo.numero,
                "escuela": self.escuela.id,
                "periodo": self.periodo_activo.id,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Lunes", response.json())
        self.assertEqual(response.json()["Lunes"][0]["curso"], self.asignatura.nombre)

    def test_uses_single_allowed_school_when_school_param_is_omitted(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("horarios:api_horarios"),
            {
                "ciclo": self.asignatura.ciclo,
                "grupo": self.grupo.numero,
                "periodo": self.periodo_activo.id,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Lunes", response.json())

    def test_requires_mandatory_cycle_and_group_parameters(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("horarios:api_horarios"))

        self.assertEqual(response.status_code, 400)
        self.assertIn("obligatorios", response.json()["error"])


class PeriodoSyncViewTests(BaseDataMixin, TestCase):
    @patch("periodos.views.call_command")
    def test_post_runs_management_command_and_returns_success_json(self, mocked_call_command):
        self.client.force_login(self.user)

        response = self.client.post(reverse("periodo_sync"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        mocked_call_command.assert_called_once()
        self.assertEqual(mocked_call_command.call_args.args[0], "sincronizar_periodos")
        self.assertIn("stdout", mocked_call_command.call_args.kwargs)

    def test_get_is_not_allowed(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("periodo_sync"))

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()["status"], "error")


class DocentesApiTests(BaseDataMixin, TestCase):
    def test_returns_empty_list_when_faculty_filter_is_missing(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("api_docentes_filtrar"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["docentes"], [])

    def test_filters_active_teachers_by_faculty(self):
        docente_inactivo = Docente.objects.create(
            apellido_paterno="RAMIREZ",
            apellido_materno="LOPEZ",
            nombres="LUIS",
            dni="87654321",
            email="luis.ramirez@example.com",
            tipo=Docente.TipoDocente.CONTRATADO,
            facultad=self.facultad,
            activo=False,
        )

        self.client.force_login(self.user)
        response = self.client.get(
            reverse("api_docentes_filtrar"),
            {"facultad_id": self.facultad.id, "estado": "activos"},
        )

        nombres = [item["nombre_completo"] for item in response.json()["docentes"]]

        self.assertIn(self.docente.nombre_completo, nombres)
        self.assertNotIn(docente_inactivo.nombre_completo, nombres)
