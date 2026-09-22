import sqlite3
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import MedicoSancionado
from core.services import normalizar_rut


FORMATO_FECHA = "%d/%m/%Y"
SOURCE_COLUMNS = {
    "rut_medico": "run_profesional_emisor",
    "nombres": "nombres_profesional_emisor",
    "apellidos": "apellidos_profesional_emisor",
    "numero_oficio": "numero_oficio",
    "fecha_oficio": "fecha_oficio",
    "monto_multa_utm": "monto_multa_utm",
    "suspension_dias": "suspension_dias",
    "inicio_suspension": "inicio_de_la_suspension_de_emision_de_lm_inclusive",
    "fin_suspension": "fin_de_la_suspension_de_emision_de_lm_inclusive",
}


def texto(valor):
    return str(valor).strip() if valor is not None else ""


def parsear_fecha(valor):
    valor = texto(valor)
    if not valor or valor == "-":
        return None
    try:
        return datetime.strptime(valor, FORMATO_FECHA).date()
    except ValueError as error:
        raise CommandError(f"Fecha de sancion invalida: {valor}") from error


def parsear_entero(valor):
    valor = texto(valor)
    if not valor or valor == "-":
        return None
    try:
        return int(valor)
    except ValueError as error:
        raise CommandError(f"Valor entero invalido en sancion: {valor}") from error


def parsear_decimal(valor):
    valor = texto(valor)
    if not valor or valor == "-":
        return None
    try:
        return Decimal(valor.replace(",", "."))
    except InvalidOperation as error:
        raise CommandError(f"Monto de multa invalido en sancion: {valor}") from error


def convertir_fila(row, indice):
    rut = normalizar_rut(row.get(SOURCE_COLUMNS["rut_medico"]))
    if not rut:
        raise CommandError(f"La sancion {indice} no tiene RUT de medico.")

    nombres = texto(row.get(SOURCE_COLUMNS["nombres"]))
    apellidos = texto(row.get(SOURCE_COLUMNS["apellidos"]))
    nombre_medico = " ".join(parte for parte in (nombres, apellidos) if parte)

    return {
        "rut_medico": rut,
        "nombre_medico": nombre_medico or rut,
        "numero_oficio": texto(row.get(SOURCE_COLUMNS["numero_oficio"])),
        "fecha_oficio": parsear_fecha(row.get(SOURCE_COLUMNS["fecha_oficio"])),
        "monto_multa_utm": parsear_decimal(
            row.get(SOURCE_COLUMNS["monto_multa_utm"])
        ),
        "suspension_dias": parsear_entero(
            row.get(SOURCE_COLUMNS["suspension_dias"])
        ),
        "inicio_suspension": parsear_fecha(
            row.get(SOURCE_COLUMNS["inicio_suspension"])
        ),
        "fin_suspension": parsear_fecha(
            row.get(SOURCE_COLUMNS["fin_suspension"])
        ),
        "fuente_url": texto(row.get("source_url")),
        "datos_origen": dict(row),
    }


class Command(BaseCommand):
    help = "Importa sanciones desde la base SQLite generada por el scraper."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="suseso.sqlite3",
            help="Ruta de la base SQLite de sanciones.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Cantidad maxima de registros a importar.",
        )

    def handle(self, *args, **options):
        source_path = Path(options["path"])
        if not source_path.exists():
            raise CommandError(f"No existe la base de sanciones: {source_path}")

        try:
            connection = sqlite3.connect(
                f"file:{source_path.resolve()}?mode=ro",
                uri=True,
            )
            connection.row_factory = sqlite3.Row
        except sqlite3.Error as error:
            raise CommandError(f"No se pudo abrir la base de sanciones: {error}") from error

        creados = 0
        actualizados = 0
        try:
            rows = connection.execute("SELECT * FROM records").fetchall()
            limit = options["limit"]
            if limit is not None:
                if limit <= 0:
                    raise CommandError("El limite debe ser mayor que cero.")
                rows = rows[:limit]
            with transaction.atomic():
                for indice, row in enumerate(rows, start=1):
                    datos = convertir_fila(dict(row), indice)
                    if not datos["fuente_url"]:
                        raise CommandError(
                            f"La sancion {indice} no tiene URL de origen."
                        )
                    identidad = {
                        "rut_medico": datos["rut_medico"],
                        "numero_oficio": datos["numero_oficio"],
                        "inicio_suspension": datos["inicio_suspension"],
                        "fin_suspension": datos["fin_suspension"],
                    }
                    valores = {
                        clave: valor
                        for clave, valor in datos.items()
                        if clave not in identidad
                    }
                    objeto, creado = MedicoSancionado.objects.update_or_create(
                        **identidad,
                        defaults=valores,
                    )
                    objeto.full_clean()
                    if creado:
                        creados += 1
                    else:
                        actualizados += 1
        except sqlite3.Error as error:
            raise CommandError(f"No se pudo leer la base de sanciones: {error}") from error
        finally:
            connection.close()

        self.stdout.write(
            self.style.SUCCESS(
                f"Importacion de sanciones completada: {creados} creados, "
                f"{actualizados} actualizados."
            )
        )
