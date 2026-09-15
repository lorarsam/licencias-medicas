from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from core.models import LicenciaMedica


DATOS_VALIDOS = {
    "medico": "Ana Ejemplo",
    "rut_medico": "12.345.678-5",
    "funcionario": "Luis Prueba",
    "rut_funcionario": "11.111.111-1",
    "dias_reposo": 7,
    "fecha_emision": "2026-01-01",
    "tipo_licencia": 1,
}


class AutenticacionYRolesTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.grupos = {
            nombre: Group.objects.create(name=nombre)
            for nombre in ("admin", "normal", "viewer")
        }
        self.usuarios = {}
        for nombre in self.grupos:
            usuario = self.user_model.objects.create_user(
                username=f"usuario_{nombre}",
                password="test-password-123",
            )
            usuario.groups.add(self.grupos[nombre])
            self.usuarios[nombre] = usuario

    def test_usuario_anonimo_es_enviado_al_login(self):
        respuesta = self.client.get(reverse("lista"))

        self.assertRedirects(
            respuesta,
            "/login/?next=/licencias/",
        )

    def test_login_crea_sesion_y_redirige_al_listado(self):
        respuesta = self.client.post(
            reverse("login"),
            {"username": "usuario_normal", "password": "test-password-123"},
        )

        self.assertRedirects(respuesta, reverse("lista"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_incorrecto_no_autentica(self):
        respuesta = self.client.post(
            reverse("login"),
            {"username": "usuario_normal", "password": "incorrecta"},
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_cierra_sesion_mediante_post(self):
        self.client.force_login(self.usuarios["normal"])

        respuesta = self.client.post(reverse("logout"))

        self.assertRedirects(respuesta, reverse("login"))
        respuesta_lista = self.client.get(reverse("lista"))
        self.assertRedirects(respuesta_lista, "/login/?next=/licencias/")

    def test_viewer_puede_consultar_pero_no_crear(self):
        self.client.force_login(self.usuarios["viewer"])

        respuesta_lista = self.client.get(reverse("lista"))
        respuesta_crear = self.client.post(reverse("crear"), DATOS_VALIDOS)

        self.assertEqual(respuesta_lista.status_code, 200)
        self.assertRedirects(respuesta_crear, reverse("lista"))
        self.assertEqual(LicenciaMedica.objects.count(), 0)

    def test_normal_puede_crear_pero_no_editar_ni_eliminar(self):
        self.client.force_login(self.usuarios["normal"])
        respuesta_crear = self.client.post(reverse("crear"), DATOS_VALIDOS)
        licencia = LicenciaMedica.objects.get()

        respuesta_editar = self.client.post(
            reverse("editar", args=(licencia.pk,)),
            {**DATOS_VALIDOS, "dias_reposo": 31},
        )
        respuesta_eliminar = self.client.post(
            reverse("eliminar", args=(licencia.pk,))
        )

        self.assertRedirects(respuesta_crear, reverse("lista"))
        self.assertRedirects(respuesta_editar, reverse("lista"))
        self.assertRedirects(respuesta_eliminar, reverse("lista"))
        licencia.refresh_from_db()
        self.assertEqual(licencia.dias_reposo, 7)
        self.assertFalse(licencia.eliminado)

    def test_admin_puede_editar_y_eliminar(self):
        licencia = LicenciaMedica.objects.create(
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
        self.client.force_login(self.usuarios["admin"])

        respuesta_editar = self.client.post(
            reverse("editar", args=(licencia.pk,)),
            {**DATOS_VALIDOS, "dias_reposo": 31},
        )
        respuesta_eliminar = self.client.post(
            reverse("eliminar", args=(licencia.pk,))
        )

        self.assertRedirects(respuesta_editar, reverse("lista"))
        self.assertRedirects(respuesta_eliminar, reverse("lista"))
        licencia.refresh_from_db()
        self.assertTrue(licencia.eliminado)
