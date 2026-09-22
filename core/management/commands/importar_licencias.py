import json
from datetime import date, datetime
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from core.models import LicenciaMedica
from solucion import formatear_rut


REQUIRED_FIELDS = {
    "medico",
    "rut_medico",
    "funcionario",
    "rut_funcionario",
    "dias_reposo",
    "fecha_emision",
    "tipo_licencia",
    "estado",
    "motivo",
}


def parsear_fecha(valor, campo, indice):
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError) as error:
        raise CommandError(
            f"El campo {campo} del registro {indice} no es una fecha valida."
        ) from error


def parsear_fecha_hora(valor, campo, indice, defecto=None):
    if not valor:
        return defecto
    try:
        return datetime.fromisoformat(valor)
    except (TypeError, ValueError) as error:
        raise CommandError(
            f"El campo {campo} del registro {indice} no es una fecha y hora valida."
        ) from error


def cargar_registros(path):
    try:
        contenido = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CommandError(f"No se pudo leer el respaldo: {path}") from error

    registros = contenido.get("registros") if isinstance(contenido, dict) else contenido
    if not isinstance(registros, list):
        raise CommandError("El respaldo debe contener una lista de registros.")
    return registros


class Command(BaseCommand):
    help = "Importa licencias sin importar contrasenas ni sesiones de usuarios."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="licencias_respaldo.json",
            help="Ruta del archivo de respaldo.",
        )

    def handle(self, *args, **options):
        source = Path(options["path"])
        if not source.exists():
            raise CommandError(f"No existe el archivo de respaldo: {source}")

        user_model = get_user_model()
        creados = 0
        actualizados = 0
        sin_usuario = 0
        with transaction.atomic():
            for indice, registro in enumerate(cargar_registros(source), start=1):
                if not isinstance(registro, dict):
                    raise CommandError(f"El registro {indice} no es un objeto JSON.")
                faltantes = REQUIRED_FIELDS - registro.keys()
                if faltantes:
                    raise CommandError(
                        f"El registro {indice} no contiene: {', '.join(sorted(faltantes))}."
                    )

                username = registro.get("creado_por")
                creado_por = (
                    user_model.objects.filter(username=username).first()
                    if username
                    else None
                )
                if username and creado_por is None:
                    sin_usuario += 1

                valores = {
                    "medico": registro["medico"],
                    "rut_medico": formatear_rut(registro["rut_medico"]),
                    "funcionario": registro["funcionario"],
                    "rut_funcionario": formatear_rut(registro["rut_funcionario"]),
                    "dias_reposo": registro["dias_reposo"],
                    "fecha_emision": parsear_fecha(
                        registro["fecha_emision"], "fecha_emision", indice
                    ),
                    "tipo_licencia": registro["tipo_licencia"],
                    "estado": registro["estado"],
                    "motivo": registro["motivo"],
                    "fecha": parsear_fecha_hora(
                        registro.get("fecha"),
                        "fecha",
                        indice,
                        timezone.now(),
                    ),
                    "eliminado": bool(registro.get("eliminado", False)),
                    "fecha_eliminacion": parsear_fecha_hora(
                        registro.get("fecha_eliminacion"),
                        "fecha_eliminacion",
                        indice,
                    ),
                    "creado_por": creado_por,
                }
                objeto, creado = LicenciaMedica.objects.update_or_create(
                    pk=registro.get("id"),
                    defaults=valores,
                )
                objeto.full_clean()
                if creado:
                    creados += 1
                else:
                    actualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Importacion completada: {creados} creadas, "
                f"{actualizados} actualizadas, {sin_usuario} sin usuario vinculado."
            )
        )
