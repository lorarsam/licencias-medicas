from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase


class UsuarioDemoCommandTests(TestCase):
    def test_crea_usuario_con_permisos_de_gestion(self):
        call_command(
            "crear_usuario_demo",
            password="Eva2backend",
            verbosity=0,
        )

        usuario = get_user_model().objects.get(username="Docente")

        self.assertTrue(usuario.check_password("Eva2backend"))
        self.assertTrue(usuario.is_active)
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
        self.assertTrue(usuario.groups.filter(name="admin").exists())
        self.assertTrue(usuario.has_perm("core.view_licenciamedica"))
        self.assertTrue(usuario.has_perm("core.add_licenciamedica"))
        self.assertTrue(usuario.has_perm("core.change_licenciamedica"))
        self.assertTrue(usuario.has_perm("core.delete_licenciamedica"))

    def test_comando_actualiza_usuario_existente_sin_duplicarlo(self):
        call_command(
            "crear_usuario_demo",
            password="clave-inicial",
            verbosity=0,
        )
        call_command(
            "crear_usuario_demo",
            password="Eva2backend",
            verbosity=0,
        )

        usuario = get_user_model().objects.get(username="Docente")

        self.assertEqual(
            get_user_model().objects.filter(username="Docente").count(),
            1,
        )
        self.assertTrue(usuario.check_password("Eva2backend"))
