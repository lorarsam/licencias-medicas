from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.staticfiles import finders
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

from core.forms import LicenciaMedicaForm
from core.models import LicenciaMedica
from solucion import (
    ESTADO_ACEPTADA,
    ESTADO_INVALIDO,
    ESTADO_RECHAZO_DIAS,
    ESTADO_RECHAZO_FECHA,
    MENSAJE_DIAS_INVALIDOS,
    MENSAJE_ENTERO_INVALIDO,
    MENSAJE_TIPO_INVALIDO,
    RUTA_ESTILOS,
    TIPOS_LICENCIA,
    crear_registro,
    main,
    pedir_datos,
)


DATOS_FORMULARIO_VALIDOS = {
    "medico": "Ana Ejemplo",
    "rut_medico": "12.345.678-5",
    "funcionario": "Luis Prueba",
    "rut_funcionario": "11.111.111-1",
    "dias_reposo": 7,
    "fecha_emision": "2026-01-01",
    "tipo_licencia": 1,
}


class SolucionConsolaTests(SimpleTestCase):
    @patch(
        "builtins.input",
        side_effect=(
            "Ana Ejemplo",
            "12.345.678-5",
            "Luis Prueba",
            "11.111.111-1",
            "texto",
            "01/01/2026",
            "fuera-de-rango",
        ),
    )
    def test_conserva_conversiones_invalidas_para_evaluarlas(self, input_mock):
        datos = pedir_datos()

        self.assertEqual(datos[4], "texto")
        self.assertEqual(datos[6], "fuera-de-rango")
        self.assertEqual(input_mock.call_count, 7)

    def test_persiste_y_tabula_entradas_no_numericas(self):
        casos = (
            (
                (
                    "Ana Ejemplo", "12.345.678-5", "Luis Prueba",
                    "11.111.111-1", "texto", "01/01/2026", 1,
                ),
                MENSAJE_DIAS_INVALIDOS,
            ),
            (
                (
                    "Ana Ejemplo", "12.345.678-5", "Luis Prueba",
                    "11.111.111-1", 7, "01/01/2026", "texto",
                ),
                MENSAJE_TIPO_INVALIDO,
            ),
        )

        for datos, motivo_esperado in casos:
            with self.subTest(motivo=motivo_esperado):
                with (
                    patch("solucion.pedir_datos", return_value=datos),
                    patch("solucion.cargar", return_value=[]),
                    patch("solucion.guardar") as guardar_mock,
                    patch("solucion.mostrar_tabulate") as tabulate_mock,
                    patch("builtins.print"),
                ):
                    main()

                registros = guardar_mock.call_args.args[0]
                self.assertEqual(registros[0]["estado"], ESTADO_INVALIDO)
                self.assertEqual(registros[0]["motivo"], motivo_esperado)
                tabulate_mock.assert_called_once_with(registros)


class LicenciaMedicaFormTests(SimpleTestCase):
    def test_convierte_fecha_y_tipo_para_el_dominio(self):
        formulario = LicenciaMedicaForm(DATOS_FORMULARIO_VALIDOS)

        self.assertTrue(formulario.is_valid(), formulario.errors)
        self.assertEqual(formulario.cleaned_data["fecha_emision"], date(2026, 1, 1))
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
            date(2026, 1, 1),
        )

    def test_normaliza_rut_sin_puntos_ni_guion(self):
        formulario = LicenciaMedicaForm(
            {
                **DATOS_FORMULARIO_VALIDOS,
                "rut_medico": "123456785",
                "rut_funcionario": "111111111",
            }
        )

        self.assertTrue(formulario.is_valid(), formulario.errors)
        self.assertEqual(formulario.cleaned_data["rut_medico"], "12.345.678-5")
        self.assertEqual(formulario.cleaned_data["rut_funcionario"], "11.111.111-1")


class LicenciaCRUDViewTests(TestCase):
    def setUp(self):
        self.url = reverse("lista")
        grupo = Group.objects.create(name="admin")
        usuario = get_user_model().objects.create_user(
            username="crud_admin",
            password="test-password-123",
        )
        usuario.groups.add(grupo)
        self.usuario = usuario
        self.client.force_login(self.usuario)

    def test_lista_lee_sqlite_y_muestra_registro(self):
        LicenciaMedica.objects.create(
            medico="Ana Ejemplo",
            rut_medico="12.345.678-5",
            funcionario="Luis Prueba",
            rut_funcionario="11.111.111-1",
            dias_reposo=7,
            fecha_emision=date(2026, 1, 1),
            tipo_licencia=1,
            estado=ESTADO_ACEPTADA,
            motivo="Licencia registrada correctamente",
        )

        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Ana Ejemplo")
        self.assertEqual(respuesta.context["metricas"][0]["valor"], 1)
        self.assertContains(respuesta, ESTADO_ACEPTADA)
        self.assertContains(respuesta, TIPOS_LICENCIA[1]["nombre"])

    def test_lista_muestra_registros_en_tabla_con_acciones(self):
        licencia = LicenciaMedica.objects.create(
            medico="Ana Ejemplo",
            rut_medico="12.345.678-5",
            funcionario="Luis Prueba",
            rut_funcionario="11.111.111-1",
            dias_reposo=7,
            fecha_emision=date(2026, 1, 1),
            tipo_licencia=1,
            estado=ESTADO_ACEPTADA,
            motivo="Licencia registrada correctamente",
        )

        respuesta = self.client.get(self.url)

        self.assertContains(respuesta, "<table")
        self.assertContains(respuesta, "Medico tratante")
        self.assertContains(respuesta, "RUT del funcionario")
        self.assertContains(respuesta, "Tipo de licencia")
        self.assertContains(respuesta, "01/01/2026")
        self.assertContains(respuesta, reverse("editar", args=[licencia.pk]))
        self.assertContains(respuesta, reverse("eliminar", args=[licencia.pk]))
        self.assertNotContains(respuesta, "license-card")

    def test_resumen_redirige_al_listado(self):
        respuesta = self.client.get(reverse("resumen"))

        self.assertRedirects(respuesta, self.url)

    def test_crear_guarda_y_aplica_decision(self):
        respuesta = self.client.post(reverse("crear"), DATOS_FORMULARIO_VALIDOS)

        self.assertRedirects(respuesta, self.url)
        licencia = LicenciaMedica.objects.get()
        self.assertEqual(licencia.estado, ESTADO_ACEPTADA)
        self.assertEqual(licencia.creado_por, self.usuario)

    def test_lista_filtra_por_usuario_creador_y_busqueda(self):
        otro_usuario = get_user_model().objects.create_user(
            username="otro_usuario",
            password="test-password-123",
        )
        for usuario, medico in (
            (self.usuario, "Ana Ejemplo"),
            (otro_usuario, "Beatriz Ejemplo"),
        ):
            LicenciaMedica.objects.create(
                medico=medico,
                rut_medico="12.345.678-5",
                funcionario="Luis Prueba",
                rut_funcionario="11.111.111-1",
                dias_reposo=7,
                fecha_emision=date(2026, 1, 1),
                tipo_licencia=1,
                estado=ESTADO_ACEPTADA,
                motivo="Licencia registrada correctamente",
                creado_por=usuario,
            )

        respuesta = self.client.get(
            self.url,
            {"q": "Ana", "creado_por": str(self.usuario.pk)},
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Ana Ejemplo")
        self.assertNotContains(respuesta, "Beatriz Ejemplo")
        self.assertEqual(respuesta.context["metricas"][0]["valor"], 1)

    def test_post_invalido_no_guarda(self):
        datos = {**DATOS_FORMULARIO_VALIDOS, "dias_reposo": "texto"}
        respuesta = self.client.post(reverse("crear"), datos)

        self.assertEqual(respuesta.status_code, 200)
        self.assertFormError(
            respuesta.context["formulario"], "dias_reposo", MENSAJE_ENTERO_INVALIDO
        )
        self.assertEqual(LicenciaMedica.objects.count(), 0)

    def test_crear_aplica_los_cuatro_resultados(self):
        casos = (
            ({}, ESTADO_ACEPTADA),
            ({"rut_medico": "12.345.678-9"}, ESTADO_INVALIDO),
            ({"fecha_emision": "2099-12-31"}, ESTADO_RECHAZO_FECHA),
            ({"dias_reposo": 31}, ESTADO_RECHAZO_DIAS),
        )

        for cambios, estado_esperado in casos:
            with self.subTest(estado=estado_esperado):
                datos = {**DATOS_FORMULARIO_VALIDOS, **cambios}
                respuesta = self.client.post(reverse("crear"), datos)

                self.assertRedirects(respuesta, self.url)
                self.assertEqual(
                    LicenciaMedica.objects.latest("id").estado,
                    estado_esperado,
                )

    def test_editar_recalcula_el_resultado(self):
        licencia = LicenciaMedica.objects.create(
            medico="Ana Ejemplo",
            rut_medico="12.345.678-5",
            funcionario="Luis Prueba",
            rut_funcionario="11.111.111-1",
            dias_reposo=7,
            fecha_emision=date(2026, 1, 1),
            tipo_licencia=1,
            estado=ESTADO_ACEPTADA,
            motivo="Licencia registrada correctamente",
        )

        respuesta = self.client.post(
            reverse("editar", args=(licencia.pk,)),
            {**DATOS_FORMULARIO_VALIDOS, "dias_reposo": 31},
        )

        self.assertRedirects(respuesta, self.url)
        licencia.refresh_from_db()
        self.assertEqual(licencia.estado, ESTADO_RECHAZO_DIAS)

    def test_eliminar_es_borrado_logico(self):
        licencia = LicenciaMedica.objects.create(
            medico="Ana Ejemplo",
            rut_medico="12.345.678-5",
            funcionario="Luis Prueba",
            rut_funcionario="11.111.111-1",
            dias_reposo=7,
            fecha_emision=date(2026, 1, 1),
            tipo_licencia=1,
            estado=ESTADO_ACEPTADA,
            motivo="Licencia registrada correctamente",
        )

        respuesta = self.client.post(reverse("eliminar", args=(licencia.pk,)))

        self.assertRedirects(respuesta, self.url)
        licencia.refresh_from_db()
        self.assertTrue(licencia.eliminado)
        self.assertEqual(LicenciaMedica.objects.filter(eliminado=False).count(), 0)

    def test_post_sin_csrf_es_rechazado(self):
        cliente_csrf = Client(enforce_csrf_checks=True)
        cliente_csrf.force_login(self.usuario)
        respuesta = cliente_csrf.post(reverse("crear"), DATOS_FORMULARIO_VALIDOS)

        self.assertEqual(respuesta.status_code, 403)

    def test_django_encuentra_hoja_de_estilos(self):
        self.assertIsNotNone(finders.find(RUTA_ESTILOS))
