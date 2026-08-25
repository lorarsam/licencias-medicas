from django.urls import path
from core import views
from solucion import NOMBRE_RUTA_RESUMEN, RUTA_RESUMEN

urlpatterns = [
    path(RUTA_RESUMEN, views.resumen, name=NOMBRE_RUTA_RESUMEN),
]
