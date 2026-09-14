import json
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import LicenciaMedica
from solucion import ARCHIVO_JSON, FORMATO_FECHA


REQUIRED_FIELDS = frozenset(
    {
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
)


def normalizar_registro(registro, indice):
    if not isinstance(registro, dict):
        raise CommandError(f"El registro {indice} no es un objeto JSON.")

    faltantes = REQUIRED_FIELDS - registro.keys()
    if faltantes:
        campos = ", ".join(sorted(faltantes))
        raise CommandError(f"El registro {indice} no contiene: {campos}.")

    campos_texto = (
        "medico",
        "rut_medico",
        "funcionario",
        "rut_funcionario",
        "estado",
        "motivo",
    )
    for campo in campos_texto:
        if not isinstance(registro[campo], str):
            raise CommandError(f"El campo {campo} del registro {indice} debe ser texto.")

    try:
        fecha_emision = datetime.strptime(
            registro["fecha_emision"], FORMATO_FECHA,
        ).date()
    except (TypeError, ValueError) as error:
        raise CommandError(
            f"La fecha del registro {indice} no usa el formato {FORMATO_FECHA}."
        ) from error

    dias_reposo = registro["dias_reposo"]
    tipo_licencia = registro["tipo_licencia"]
    if isinstance(dias_reposo, bool) or not isinstance(dias_reposo, int):
        raise CommandError(f"Los dias del registro {indice} deben ser enteros.")
    if isinstance(tipo_licencia, bool) or not isinstance(tipo_licencia, int):
        raise CommandError(f"El tipo del registro {indice} debe ser un entero.")

    datos = {
        "medico": registro["medico"],
        "rut_medico": registro["rut_medico"],
        "funcionario": registro["funcionario"],
        "rut_funcionario": registro["rut_funcionario"],
        "dias_reposo": dias_reposo,
        "fecha_emision": fecha_emision,
        "tipo_licencia": tipo_licencia,
        "estado": registro["estado"],
        "motivo": registro["motivo"],
        "eliminado": False,
        "fecha_eliminacion": None,
    }

    try:
        LicenciaMedica(**datos).full_clean()
    except ValidationError as error:
        raise CommandError(f"El registro {indice} no es valido: {error}") from error

    return datos


class Command(BaseCommand):
    help = "Importa los registros existentes desde datos.json a SQLite."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default=str(ARCHIVO_JSON),
            help="Ruta del archivo JSON de origen.",
        )

    def handle(self, *args, **options):
        source_path = Path(options["path"])
        if not source_path.exists():
            raise CommandError(f"No existe el archivo de origen: {source_path}")

        try:
            with source_path.open("r", encoding="utf-8") as source_file:
                registros = json.load(source_file)
        except json.JSONDecodeError as error:
            raise CommandError(f"El archivo JSON no es valido: {error}") from error

        if not isinstance(registros, list):
            raise CommandError("El archivo JSON debe contener una lista de registros.")

        creados = 0
        existentes = 0
        with transaction.atomic():
            for indice, registro in enumerate(registros, start=1):
                datos = normalizar_registro(registro, indice)
                _, creado = LicenciaMedica.objects.get_or_create(**datos)
                if creado:
                    creados += 1
                else:
                    existentes += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Importacion completada: {creados} creados, "
                f"{existentes} ya existentes."
            )
        )
