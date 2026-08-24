from django.shortcuts import render
from solucion import (
    CLASE_ESTADO_DESCONOCIDO,
    CLASES_ESTADO,
    NOMBRE_TIPO_DESCONOCIDO,
    TIPOS_LICENCIA,
    cargar,
    decidir,
)


def resumen(request):
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
        registros.append(registro)
    return render(request, "resumen.html", {"registros": registros})
