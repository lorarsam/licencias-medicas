from django.shortcuts import redirect, render
from django.urls import reverse

from core.forms import LicenciaMedicaForm
from solucion import (
    CLASE_ESTADO_DESCONOCIDO,
    CLASE_INDICADOR_TOTAL,
    CLASES_ESTADO,
    ENCABEZADOS_TABLA,
    ESTADO_ACEPTADA,
    ESTADO_INVALIDO,
    ESTADO_RECHAZO_DIAS,
    ESTADO_RECHAZO_FECHA,
    METODO_POST,
    NOMBRE_RUTA_RESUMEN,
    NOMBRE_TIPO_DESCONOCIDO,
    PARAMETRO_REGISTRO_GUARDADO,
    PLANTILLA_RESUMEN,
    RUTA_ESTILOS,
    TEXTOS_WEB,
    TIPOS_LICENCIA,
    VALOR_PARAMETRO_ACTIVO,
    cargar,
    crear_registro,
    decidir,
    guardar,
)


def resumen(request):
    formulario = LicenciaMedicaForm(request.POST or None)
    if request.method == METODO_POST and formulario.is_valid():
        registros_guardados = cargar()
        registros_guardados.append(crear_registro(**formulario.cleaned_data))
        guardar(registros_guardados)
        destino = reverse(NOMBRE_RUTA_RESUMEN)
        return redirect(
            f"{destino}?{PARAMETRO_REGISTRO_GUARDADO}={VALOR_PARAMETRO_ACTIVO}"
        )

    conteos = {
        ESTADO_ACEPTADA: 0,
        ESTADO_RECHAZO_FECHA: 0,
        ESTADO_RECHAZO_DIAS: 0,
        ESTADO_INVALIDO: 0,
    }
    registros = []
    for registro_guardado in cargar():
        registro = registro_guardado.copy()
        registro["estado"], registro["motivo"] = decidir(
            registro.get("medico"),
            registro.get("rut_medico"),
            registro.get("funcionario"),
            registro.get("rut_funcionario"),
            registro.get("dias_reposo"),
            registro.get("fecha_emision"),
            registro.get("tipo_licencia"),
        )
        tipo = registro.get("tipo_licencia")
        if tipo in TIPOS_LICENCIA:
            registro["tipo_nombre"] = TIPOS_LICENCIA[tipo]["nombre"]
        else:
            registro["tipo_nombre"] = NOMBRE_TIPO_DESCONOCIDO
        registro["estado_clase"] = CLASES_ESTADO.get(
            registro["estado"], CLASE_ESTADO_DESCONOCIDO,
        )
        if registro["estado"] in conteos:
            conteos[registro["estado"]] += 1
        registros.append(registro)

    metricas = (
        {
            "etiqueta": TEXTOS_WEB["indicador_total"],
            "valor": len(registros),
            "clase": CLASE_INDICADOR_TOTAL,
        },
        {
            "etiqueta": TEXTOS_WEB["indicador_aceptadas"],
            "valor": conteos[ESTADO_ACEPTADA],
            "clase": CLASES_ESTADO[ESTADO_ACEPTADA],
        },
        {
            "etiqueta": TEXTOS_WEB["indicador_rechazadas"],
            "valor": conteos[ESTADO_RECHAZO_FECHA] + conteos[ESTADO_RECHAZO_DIAS],
            "clase": CLASES_ESTADO[ESTADO_RECHAZO_FECHA],
        },
        {
            "etiqueta": TEXTOS_WEB["indicador_invalidas"],
            "valor": conteos[ESTADO_INVALIDO],
            "clase": CLASES_ESTADO[ESTADO_INVALIDO],
        },
    )
    contexto = {
        "encabezados": ENCABEZADOS_TABLA,
        "formulario": formulario,
        "guardada": (
            request.GET.get(PARAMETRO_REGISTRO_GUARDADO)
            == VALOR_PARAMETRO_ACTIVO
        ),
        "metricas": metricas,
        "nombre_ruta_resumen": NOMBRE_RUTA_RESUMEN,
        "registros": registros,
        "ruta_estilos": RUTA_ESTILOS,
        "ui": TEXTOS_WEB,
    }
    return render(request, PLANTILLA_RESUMEN, contexto)
