from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from core.decorators import requiere_rol
from core.forms import InicioSesionForm, LicenciaMedicaForm
from core.models import LicenciaMedica
from solucion import (
    CLASE_ESTADO_DESCONOCIDO,
    CLASE_INDICADOR_TOTAL,
    CLASES_ESTADO,
    ESTADO_ACEPTADA,
    ESTADO_INVALIDO,
    ESTADO_RECHAZO_DIAS,
    ESTADO_RECHAZO_FECHA,
    FORMATO_FECHA,
    METODO_POST,
    RUTA_ESTILOS,
    TEXTOS_WEB,
    decidir,
)


def _contexto_base(**extra):
    contexto = {
        "nombre_ruta_resumen": "lista",
        "ruta_estilos": RUTA_ESTILOS,
        "ui": {**TEXTOS_WEB, "pie": "Persistencia en SQLite"},
    }
    contexto.update(extra)
    return contexto


def _evaluar_licencia(licencia):
    estado, motivo = decidir(
        licencia.medico,
        licencia.rut_medico,
        licencia.funcionario,
        licencia.rut_funcionario,
        licencia.dias_reposo,
        licencia.fecha_emision.strftime(FORMATO_FECHA),
        licencia.tipo_licencia,
    )
    licencia.estado = estado
    licencia.motivo = motivo


def _fila_licencia(licencia):
    return {
        "id": licencia.pk,
        "medico": licencia.medico,
        "rut_medico": licencia.rut_medico,
        "funcionario": licencia.funcionario,
        "rut_funcionario": licencia.rut_funcionario,
        "dias_reposo": licencia.dias_reposo,
        "fecha_emision": licencia.fecha_emision,
        "tipo_licencia": licencia.tipo_licencia,
        "tipo_nombre": licencia.get_tipo_licencia_display(),
        "estado": licencia.estado,
        "estado_clase": CLASES_ESTADO.get(
            licencia.estado, CLASE_ESTADO_DESCONOCIDO,
        ),
        "motivo": licencia.motivo,
    }


def _metricas(registros):
    conteos = {
        ESTADO_ACEPTADA: 0,
        ESTADO_RECHAZO_FECHA: 0,
        ESTADO_RECHAZO_DIAS: 0,
        ESTADO_INVALIDO: 0,
    }
    for registro in registros:
        if registro.estado in conteos:
            conteos[registro.estado] += 1

    return (
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


@require_http_methods(["GET", METODO_POST])
def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect("lista")

    formulario = InicioSesionForm(request, data=request.POST or None)
    if request.method == METODO_POST and formulario.is_valid():
        login(request, formulario.get_user())
        return redirect("lista")

    return render(
        request,
        "login.html",
        _contexto_base(formulario=formulario),
    )


@require_POST
@login_required(login_url="login")
def cerrar_sesion(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
@require_GET
def resumen(request):
    return redirect("lista")


@login_required(login_url="login")
@require_GET
def lista(request):
    registros = list(
        LicenciaMedica.objects.filter(eliminado=False)
    )
    contexto = _contexto_base(
        encabezados={
            "medico": "Medico",
            "rut_medico": "RUT medico",
            "funcionario": "Funcionario",
            "rut_funcionario": "RUT funcionario",
            "dias_reposo": "Dias",
            "fecha_emision": "Fecha",
            "tipo_licencia": "Tipo",
            "estado": "Estado",
            "motivo": "Motivo",
        },
        metricas=_metricas(registros),
        registros=[_fila_licencia(registro) for registro in registros],
    )
    return render(request, "lista.html", contexto)


@requiere_rol("admin", "normal")
@require_http_methods(["GET", METODO_POST])
def crear(request):
    formulario = LicenciaMedicaForm(request.POST or None)
    if request.method == METODO_POST and formulario.is_valid():
        licencia = formulario.save(commit=False)
        _evaluar_licencia(licencia)
        licencia.save()
        messages.success(request, "Licencia creada correctamente.")
        return redirect("lista")

    return render(
        request,
        "licencia_form.html",
        _contexto_base(formulario=formulario, accion="Crear"),
    )


@requiere_rol("admin")
@require_http_methods(["GET", METODO_POST])
def editar(request, pk):
    licencia = get_object_or_404(
        LicenciaMedica,
        pk=pk,
        eliminado=False,
    )
    formulario = LicenciaMedicaForm(request.POST or None, instance=licencia)
    if request.method == METODO_POST and formulario.is_valid():
        licencia = formulario.save(commit=False)
        _evaluar_licencia(licencia)
        licencia.save()
        messages.success(request, "Licencia actualizada correctamente.")
        return redirect("lista")

    return render(
        request,
        "licencia_form.html",
        _contexto_base(
            formulario=formulario,
            accion="Editar",
            licencia=licencia,
        ),
    )


@requiere_rol("admin")
@require_http_methods(["GET", METODO_POST])
def eliminar(request, pk):
    licencia = get_object_or_404(
        LicenciaMedica,
        pk=pk,
        eliminado=False,
    )
    if request.method == METODO_POST:
        licencia.soft_delete()
        messages.success(request, "Licencia eliminada correctamente.")
        return redirect("lista")

    return render(
        request,
        "licencia_confirmar_eliminacion.html",
        _contexto_base(licencia=licencia),
    )
