from django.urls import path
from core import views

urlpatterns = [
    path("resumen/", views.resumen, name="resumen"),
]
