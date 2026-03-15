from django.test import TestCase
from django.urls import reverse

from .utils import BaseDataMixin


class CoreRoutesSmokeTests(BaseDataMixin, TestCase):
    def test_anonymous_users_are_redirected_from_protected_pages(self):
        protected_urls = [
            reverse("home"),
            reverse("aula_list"),
            reverse("docente_list"),
            reverse("planes_list"),
            reverse("periodo_list"),
            reverse("horarios:horario_asignaturas"),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("login"), response.url)

    def test_authenticated_user_can_load_core_pages(self):
        self.client.force_login(self.user)
        pages = [
            reverse("home"),
            reverse("aula_list"),
            reverse("docente_list"),
            reverse("planes_list"),
            reverse("periodo_list"),
            reverse("horarios:horario_asignaturas"),
        ]

        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
