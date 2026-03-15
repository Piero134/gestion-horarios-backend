from django.test import TestCase
from django.urls import reverse

from docentes.models import Docente

from .utils import BaseDataMixin


class DocentesCrudViewsTests(BaseDataMixin, TestCase):
    def test_create_docente_persists_cleaned_values(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("docente_create"),
            {
                "tipo": Docente.TipoDocente.NOMBRADO,
                "dni": "11223344",
                "apellido_paterno": "ramos",
                "apellido_materno": "diaz",
                "nombres": "luz marina",
                "email": "luz@example.com",
                "facultad": self.facultad.id,
                "departamento": self.departamento.id,
                "codigo": "DOC-002",
                "categoria": Docente.Categoria.AUXILIAR,
                "dedicacion": Docente.Dedicacion.TIEMPO_COMPLETO,
            },
        )

        self.assertRedirects(response, reverse("docente_list"))
        docente = Docente.objects.get(dni="11223344")
        self.assertEqual(docente.apellido_paterno, "RAMOS")
        self.assertEqual(docente.nombres, "LUZ MARINA")

    def test_edit_docente_updates_record(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("docente_edit", kwargs={"pk": self.docente.pk}),
            {
                "tipo": self.docente.tipo,
                "dni": self.docente.dni,
                "apellido_paterno": self.docente.apellido_paterno,
                "apellido_materno": self.docente.apellido_materno,
                "nombres": "ANA MARIA",
                "email": self.docente.email,
                "facultad": self.facultad.id,
                "departamento": self.departamento.id,
                "codigo": self.docente.codigo,
                "categoria": self.docente.categoria,
                "dedicacion": self.docente.dedicacion,
            },
        )

        self.assertRedirects(response, reverse("docente_list"))
        self.docente.refresh_from_db()
        self.assertEqual(self.docente.nombres, "ANA MARIA")

    def test_toggle_estado_deactivates_docente(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("docente_toggle_estado", kwargs={"pk": self.docente.pk}))

        self.assertRedirects(response, reverse("docente_list"))
        self.docente.refresh_from_db()
        self.assertFalse(self.docente.activo)

    def test_legacy_delete_redirects_to_toggle_estado(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("docente_delete", kwargs={"pk": self.docente.pk}))

        self.assertRedirects(
            response,
            reverse("docente_toggle_estado", kwargs={"pk": self.docente.pk}),
        )
