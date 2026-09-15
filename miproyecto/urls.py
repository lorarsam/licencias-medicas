from django.contrib import admin
from django.urls import path
from core import views
from solucion import NOMBRE_RUTA_RESUMEN, RUTA_RESUMEN

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", views.iniciar_sesion, name="login"),
    path("logout/", views.cerrar_sesion, name="logout"),
    path("licencias/", views.lista, name="lista"),
    path("licencias/crear/", views.crear, name="crear"),
    path("licencias/<int:pk>/editar/", views.editar, name="editar"),
    path("licencias/<int:pk>/eliminar/", views.eliminar, name="eliminar"),
    path(RUTA_RESUMEN, views.resumen, name=NOMBRE_RUTA_RESUMEN),
]
