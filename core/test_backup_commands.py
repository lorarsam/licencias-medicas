import json
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from core.models import LicenciaMedica


class RespaldoLicenciasTests(TestCase):
    def test_exporta_e_importa_sin_contrasenas_y_con_usuario(self):
        usuario = get_user_model().objects.create_user(
            username="docente_respaldo",
            password="secreto-de-prueba",
        )
        licencia = LicenciaMedica.objects.create(
            medico="Ana Ejemplo",
            rut_medico="123456785",
            funcionario="Luis Prueba",
            rut_funcionario="111111111",
            dias_reposo=7,
            fecha_emision=date(2026, 1, 1),
            tipo_licencia=1,
            estado="Aceptada",
            motivo="Licencia registrada correctamente",
            creado_por=usuario,
        )

        with TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "respaldo.json"
            call_command("exportar_licencias", path=str(path), verbosity=0)
            contenido = json.loads(path.read_text(encoding="utf-8"))

            self.assertNotIn("secreto-de-prueba", path.read_text(encoding="utf-8"))
            self.assertEqual(contenido["registros"][0]["creado_por"], usuario.username)

            licencia_pk = licencia.pk
            licencia.delete()
            call_command("importar_licencias", path=str(path), verbosity=0)

        licencia_restaurada = LicenciaMedica.objects.get(pk=licencia_pk)
        self.assertEqual(licencia_restaurada.rut_medico, "12.345.678-5")
        self.assertEqual(licencia_restaurada.creado_por, usuario)
