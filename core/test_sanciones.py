import sqlite3
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from core.constants import ESTADO_RECHAZO_SANCION
from core.models import MedicoSancionado, LicenciaMedica
from core.services import buscar_sancion_activa, evaluar_licencia


DATOS_LICENCIA = {
    "medico": "Medico de prueba",
    "rut_medico": "15.800.526-3",
    "funcionario": "Funcionario de prueba",
    "rut_funcionario": "11.111.111-1",
    "dias_reposo": 7,
    "fecha_emision": "2026-09-16",
    "tipo_licencia": 1,
}


class SancionesTests(TestCase):
    def setUp(self):
        grupo = Group.objects.create(name="admin")
        usuario = get_user_model().objects.create_user(
            username="sanciones_admin",
            password="test-password-123",
        )
        usuario.groups.add(grupo)
        self.client.force_login(usuario)
        MedicoSancionado.objects.create(
            rut_medico="158005263",
            nombre_medico="Medico de prueba",
            numero_oficio="OFICIO-PRUEBA",
            fecha_oficio=date(2026, 9, 10),
            suspension_dias=30,
            inicio_suspension=date(2026, 9, 15),
            fin_suspension=date(2026, 10, 14),
            fuente_url="https://example.com/sanciones",
        )

    def test_reconoce_rut_con_puntos_y_guion_durante_la_suspension(self):
        sancion = buscar_sancion_activa(
            "15.800.526-3",
            date(2026, 9, 16),
        )

        self.assertIsNotNone(sancion)
        self.assertEqual(sancion.rut_medico, "158005263")

    def test_los_limites_de_la_suspension_son_inclusivos(self):
        self.assertIsNotNone(
            buscar_sancion_activa("158005263", date(2026, 9, 15))
        )
        self.assertIsNotNone(
            buscar_sancion_activa("158005263", date(2026, 10, 14))
        )
        self.assertIsNone(
            buscar_sancion_activa("158005263", date(2026, 10, 15))
        )

    def test_evaluacion_rechaza_medico_sancionado(self):
        estado, motivo, sancion = evaluar_licencia(
            "Medico de prueba",
            "15.800.526-3",
            "Funcionario de prueba",
            "11.111.111-1",
            7,
            "16/09/2026",
            1,
        )

        self.assertEqual(estado, ESTADO_RECHAZO_SANCION)
        self.assertIn("sancionado", motivo)
        self.assertIsNotNone(sancion)

    def test_creacion_guarda_rechazo_y_muestra_situacion(self):
        respuesta = self.client.post(
            reverse("crear"),
            DATOS_LICENCIA,
        )

        self.assertRedirects(respuesta, reverse("lista"))
        licencia = LicenciaMedica.objects.get()
        self.assertEqual(licencia.estado, ESTADO_RECHAZO_SANCION)

        listado = self.client.get(reverse("lista"))
        self.assertContains(listado, "Medico sancionado")
        self.assertContains(listado, ESTADO_RECHAZO_SANCION)

    def test_rechazo_previo_no_es_reemplazado_por_sancion(self):
        estado, _, sancion = evaluar_licencia(
            "Medico de prueba",
            "15.800.526-9",
            "Funcionario de prueba",
            "11.111.111-1",
            7,
            "16/09/2026",
            1,
        )

        self.assertNotEqual(estado, ESTADO_RECHAZO_SANCION)
        self.assertIsNone(sancion)


class ImportarSancionesLimitTests(TestCase):
    def test_importa_solo_el_limite_solicitado(self):
        with TemporaryDirectory() as temporary_directory:
            base = Path(temporary_directory) / "suseso.sqlite3"
            connection = sqlite3.connect(base)
            connection.execute(
                """
                CREATE TABLE records (
                    run_profesional_emisor TEXT,
                    nombres_profesional_emisor TEXT,
                    apellidos_profesional_emisor TEXT,
                    numero_oficio TEXT,
                    fecha_oficio TEXT,
                    monto_multa_utm TEXT,
                    suspension_dias TEXT,
                    inicio_de_la_suspension_de_emision_de_lm_inclusive TEXT,
                    fin_de_la_suspension_de_emision_de_lm_inclusive TEXT,
                    source_url TEXT
                )
                """
            )
            for rut, oficio in (
                ("11.111.111-1", "OFICIO-UNO"),
                ("22.222.222-2", "OFICIO-DOS"),
                ("33.333.333-3", "OFICIO-TRES"),
            ):
                connection.execute(
                    "INSERT INTO records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        rut,
                        "Nombre",
                        "Apellido",
                        oficio,
                        "01/09/2026",
                        "1000",
                        "30",
                        "01/09/2026",
                        "30/09/2026",
                        "https://example.com/sanciones",
                    ),
                )
            connection.commit()
            connection.close()

            call_command(
                "importar_sanciones",
                path=str(base),
                limit=2,
                verbosity=0,
            )

        self.assertEqual(MedicoSancionado.objects.count(), 2)
        self.assertEqual(
            set(MedicoSancionado.objects.values_list("numero_oficio", flat=True)),
            {"OFICIO-UNO", "OFICIO-DOS"},
        )
