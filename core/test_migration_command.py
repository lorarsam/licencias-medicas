import json
from datetime import date
from tempfile import TemporaryDirectory
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from core.models import LicenciaMedica


class CargarDatosCommandTests(TestCase):
    def test_importa_y_no_duplica_registros(self):
        registro = {
            "medico": "Ana Ejemplo",
            "rut_medico": "12.345.678-5",
            "funcionario": "Luis Prueba",
            "rut_funcionario": "11.111.111-1",
            "dias_reposo": 7,
            "fecha_emision": "01/01/2026",
            "tipo_licencia": 1,
            "estado": "Aceptada",
            "motivo": "Licencia registrada correctamente",
        }

        with TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "datos.json"
            path.write_text(json.dumps([registro]), encoding="utf-8")

            call_command("cargar_datos", path=str(path))
            call_command("cargar_datos", path=str(path))

        self.assertEqual(LicenciaMedica.objects.count(), 1)
        licencia = LicenciaMedica.objects.get()
        self.assertEqual(licencia.fecha_emision, date(2026, 1, 1))
        self.assertEqual(licencia.tipo_licencia, 1)
        self.assertEqual(licencia.estado, "Aceptada")
