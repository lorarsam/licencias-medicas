from datetime import date
from unittest.mock import patch

from django.contrib.staticfiles import finders
from django.test import Client, SimpleTestCase
from django.urls import reverse

from core.forms import LicenciaMedicaForm
from solucion import (
    ESTADO_ACEPTADA,
    ESTADO_INVALIDO,
    ESTADO_RECHAZO_DIAS,
    ESTADO_RECHAZO_FECHA,
    FORMATO_FECHA,
    MENSAJE_ENTERO_INVALIDO,
    NOMBRE_RUTA_RESUMEN,
    PARAMETRO_REGISTRO_GUARDADO,
    RUTA_ESTILOS,
    TEXTOS_WEB,
    TIPOS_LICENCIA,
    VALOR_PARAMETRO_ACTIVO,
    crear_registro,
)


DATOS_FORMULARIO_VALIDOS = {
    "nombre_medico": "Ana Ejemplo",
    "rut_medico": "12.345.678-5",
    "nombre_funcionario": "Luis Prueba",
    "rut_funcionario": "11.111.111-1",
    "dias_reposo": 7,
    "fecha_emision": "2026-01-01",
    "tipo_licencia": 1,
}


class LicenciaMedicaFormTests(SimpleTestCase):
    def test_convierte_fecha_y_tipo_para_el_dominio(self):
        formulario = LicenciaMedicaForm(DATOS_FORMULARIO_VALIDOS)

        self.assertTrue(formulario.is_valid(), formulario.errors)
        self.assertEqual(formulario.cleaned_data["fecha_emision"], "01/01/2026")
        self.assertIsInstance(formulario.cleaned_data["tipo_licencia"], int)

    def test_opciones_se_generan_desde_catalogo_de_licencias(self):
        formulario = LicenciaMedicaForm()
        codigos_formulario = {
            opcion[0] for opcion in formulario.fields["tipo_licencia"].choices
            if opcion[0] != ""
        }

        self.assertEqual(codigos_formulario, set(TIPOS_LICENCIA))

    def test_informa_error_de_conversion_sin_aplicar_reglas_de_dominio(self):
        datos = {**DATOS_FORMULARIO_VALIDOS, "dias_reposo": "texto"}
        formulario = LicenciaMedicaForm(datos)

        self.assertFalse(formulario.is_valid())
        self.assertIn("dias_reposo", formulario.errors)

    def test_normaliza_fecha_con_formato_centralizado(self):
        formulario = LicenciaMedicaForm(DATOS_FORMULARIO_VALIDOS)

        self.assertTrue(formulario.is_valid(), formulario.errors)
        self.assertEqual(
            formulario.cleaned_data["fecha_emision"],
            date(2026, 1, 1).strftime(FORMATO_FECHA),
        )


class ResumenViewTests(SimpleTestCase):
    def setUp(self):
        self.url = reverse(NOMBRE_RUTA_RESUMEN)

    def test_get_muestra_formulario_y_estado_vacio(self):
        with patch("core.views.cargar", return_value=[]):
            respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, TEXTOS_WEB["seccion_formulario"])
        self.assertContains(respuesta, TEXTOS_WEB["sin_registros"])
        self.assertEqual(respuesta.context["registros"], [])
        self.assertEqual(respuesta.context["metricas"][0]["valor"], 0)

    def test_get_prepara_registro_tipo_estado_y_conteos(self):
        registro = crear_registro(
            "Ana Ejemplo",
            "12.345.678-5",
            "Luis Prueba",
            "11.111.111-1",
            7,
            "01/01/2026",
            1,
        )
        with patch("core.views.cargar", return_value=[registro]):
            respuesta = self.client.get(self.url)

        registro_renderizado = respuesta.context["registros"][0]
        self.assertEqual(registro_renderizado["estado"], ESTADO_ACEPTADA)
        self.assertEqual(
            registro_renderizado["tipo_nombre"], TIPOS_LICENCIA[1]["nombre"]
        )
        self.assertEqual(respuesta.context["metricas"][0]["valor"], 1)
        self.assertEqual(respuesta.context["metricas"][1]["valor"], 1)
        self.assertContains(respuesta, ESTADO_ACEPTADA)
        self.assertContains(respuesta, TIPOS_LICENCIA[1]["nombre"])

    def test_post_invalido_muestra_errores_y_no_guarda(self):
        datos = {**DATOS_FORMULARIO_VALIDOS, "dias_reposo": "texto"}
        with (
            patch("core.views.cargar", return_value=[]),
            patch("core.views.guardar") as guardar_mock,
        ):
            respuesta = self.client.post(self.url, datos)

        self.assertEqual(respuesta.status_code, 200)
        self.assertFormError(
            respuesta.context["formulario"], "dias_reposo", MENSAJE_ENTERO_INVALIDO
        )
        guardar_mock.assert_not_called()

    def test_post_aplica_los_cuatro_resultados_y_redirige(self):
        casos = (
            ({}, ESTADO_ACEPTADA),
            ({"rut_medico": "12.345.678-9"}, ESTADO_INVALIDO),
            ({"fecha_emision": "2099-12-31"}, ESTADO_RECHAZO_FECHA),
            ({"dias_reposo": 31}, ESTADO_RECHAZO_DIAS),
        )

        for cambios, estado_esperado in casos:
            with self.subTest(estado=estado_esperado):
                datos = {**DATOS_FORMULARIO_VALIDOS, **cambios}
                with (
                    patch("core.views.cargar", return_value=[]),
                    patch("core.views.guardar") as guardar_mock,
                ):
                    respuesta = self.client.post(self.url, datos)

                self.assertEqual(respuesta.status_code, 302)
                self.assertEqual(
                    respuesta.url,
                    (
                        f"{self.url}?{PARAMETRO_REGISTRO_GUARDADO}="
                        f"{VALOR_PARAMETRO_ACTIVO}"
                    ),
                )
                registros_guardados = guardar_mock.call_args.args[0]
                self.assertEqual(registros_guardados[0]["estado"], estado_esperado)

    def test_post_sin_csrf_es_rechazado_sin_guardar(self):
        cliente_csrf = Client(enforce_csrf_checks=True)
        with (
            patch("core.views.cargar", return_value=[]),
            patch("core.views.guardar") as guardar_mock,
        ):
            respuesta = cliente_csrf.post(self.url, DATOS_FORMULARIO_VALIDOS)

        self.assertEqual(respuesta.status_code, 403)
        guardar_mock.assert_not_called()

    def test_post_con_csrf_valido_guarda_y_redirige(self):
        cliente_csrf = Client(enforce_csrf_checks=True)
        with patch("core.views.cargar", return_value=[]):
            respuesta_get = cliente_csrf.get(self.url)
        token = respuesta_get.cookies["csrftoken"].value
        datos = {**DATOS_FORMULARIO_VALIDOS, "csrfmiddlewaretoken": token}

        with (
            patch("core.views.cargar", return_value=[]),
            patch("core.views.guardar") as guardar_mock,
        ):
            respuesta_post = cliente_csrf.post(self.url, datos)

        self.assertEqual(respuesta_post.status_code, 302)
        guardar_mock.assert_called_once()

    def test_muestra_confirmacion_solo_con_parametro_centralizado(self):
        url = (
            f"{self.url}?{PARAMETRO_REGISTRO_GUARDADO}="
            f"{VALOR_PARAMETRO_ACTIVO}"
        )
        with patch("core.views.cargar", return_value=[]):
            respuesta = self.client.get(url)

        self.assertContains(respuesta, TEXTOS_WEB["confirmacion"])

    def test_django_encuentra_hoja_de_estilos(self):
        self.assertIsNotNone(finders.find(RUTA_ESTILOS))
