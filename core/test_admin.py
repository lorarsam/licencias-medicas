from datetime import date

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.admin import LicenciaMedicaAdmin
from core.models import LicenciaMedica


class LicenciaMedicaAdminTests(TestCase):
    def test_modelo_registrado_con_columnas_filtros_y_busqueda(self):
        configuracion = admin.site._registry[LicenciaMedica]

        self.assertIsInstance(configuracion, LicenciaMedicaAdmin)
        self.assertIn("funcionario", configuracion.list_display)
        self.assertIn("estado", configuracion.list_filter)
        self.assertIn("eliminado", configuracion.list_filter)
        self.assertIn("rut_medico", configuracion.search_fields)
        self.assertIn("fecha", configuracion.readonly_fields)

    def test_superusuario_puede_abrir_el_listado(self):
        user_model = get_user_model()
        usuario = user_model.objects.create_superuser(
            username="admin_test",
            email="admin@example.com",
            password="test-password-123",
        )
        LicenciaMedica.objects.create(
            medico="Ana Ejemplo",
            rut_medico="12.345.678-5",
            funcionario="Luis Prueba",
            rut_funcionario="11.111.111-1",
            dias_reposo=7,
            fecha_emision=date(2026, 1, 1),
            tipo_licencia=1,
            estado="Aceptada",
            motivo="Licencia registrada correctamente",
        )

        self.client.force_login(usuario)
        response = self.client.get(
            reverse("admin:core_licenciamedica_changelist")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Luis Prueba")
