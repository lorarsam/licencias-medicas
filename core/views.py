import json
import os
from django.shortcuts import render
from solucion import ARCHIVO_JSON, TIPOS_LICENCIA, cargar


def resumen(request):
    registros = cargar()
    for registro in registros:
        tipo = registro.get("tipo_licencia")
        if tipo in TIPOS_LICENCIA:
            registro["tipo_nombre"] = TIPOS_LICENCIA[tipo]["nombre"]
        else:
            registro["tipo_nombre"] = "Desconocido"
    return render(request, "resumen.html", {"registros": registros})
