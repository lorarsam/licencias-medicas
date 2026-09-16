"""Descarga y persiste registros de sanciones publicados por SUSESO.

El scraper no depende de los valores actuales de la tabla. Lee los encabezados
del HTML, crea las columnas SQLite necesarias y conserva los datos originales
de cada fila en JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import unicodedata
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup, Tag


DEFAULT_URL = "https://www.suseso.gob.cl/609/w3-propertyvalue-799701.html"
DEFAULT_DATABASE = "suseso.sqlite3"
DEFAULT_TIMEOUT = 30
DEFAULT_USER_AGENT = "SUSESO-public-records-scraper/1.0"


@dataclass(frozen=True)
class TableRecord:
    """Una fila de la tabla y su representación original."""

    values: dict[str, str | None]
    cells: list[dict[str, Any]]
    html: str
    row_hash: str


@dataclass(frozen=True)
class PageData:
    """Contenido extraído de una página."""

    title: str
    description: str
    headers: list[str]
    column_names: list[str]
    records: list[TableRecord]


def clean_text(value: str) -> str:
    """Normaliza espacios sin modificar el contenido legible."""

    return re.sub(r"\s+", " ", value).strip()


def slugify(value: str) -> str:
    """Convierte un encabezado en un identificador SQLite estable."""

    ascii_value = unicodedata.normalize("NFKD", value)
    ascii_value = ascii_value.encode("ascii", "ignore").decode("ascii")
    result = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_value.lower()).strip("_")
    return result or "columna"


def unique_column_names(headers: list[str]) -> list[str]:
    """Genera nombres únicos manteniendo el orden de los encabezados."""

    used: Counter[str] = Counter()
    names: list[str] = []
    for header in headers:
        base = slugify(header)
        used[base] += 1
        names.append(base if used[base] == 1 else f"{base}_{used[base]}")
    return names


def quote_identifier(identifier: str) -> str:
    """Escapa un identificador generado antes de usarlo en SQL."""

    return '"' + identifier.replace('"', '""') + '"'


def table_headers(table: Tag) -> list[str]:
    thead = table.find("thead")
    if not thead:
        return []
    header_row = thead.find("tr")
    if not header_row:
        return []
    return [clean_text(cell.get_text(" ", strip=True)) for cell in header_row.find_all(("th", "td"), recursive=False)]


def find_data_table(soup: BeautifulSoup, selector: str | None = None) -> Tag:
    """Obtiene la tabla con datos, explícita o por detección de contenido."""

    if selector:
        table = soup.select_one(selector)
        if not table:
            raise ValueError(f"No se encontró la tabla usando el selector: {selector}")
        return table

    candidates: list[tuple[int, Tag]] = []
    for table in soup.find_all("table"):
        headers = table_headers(table)
        rows = table.select("tbody tr")
        if headers and rows:
            candidates.append((len(rows), table))

    if not candidates:
        raise ValueError("No se encontró ninguna tabla HTML con encabezados y filas")
    return max(candidates, key=lambda item: item[0])[1]


def extract_cell(cell: Tag) -> dict[str, Any]:
    return {
        "value": clean_text(cell.get_text(" ", strip=True)) or None,
        "links": [
            {"text": clean_text(link.get_text(" ", strip=True)), "href": link.get("href")}
            for link in cell.find_all("a")
        ],
        "html": str(cell),
    }


def extract_page(html: str, table_selector: str | None = None) -> PageData:
    """Extrae metadatos y todas las filas de la tabla seleccionada."""

    soup = BeautifulSoup(html, "html.parser")
    table = find_data_table(soup, table_selector)
    headers = table_headers(table)
    rows = table.select("tbody tr")

    max_cells = max((len(row.find_all(("td", "th"), recursive=False)) for row in rows), default=0)
    while len(headers) < max_cells:
        headers.append(f"Columna {len(headers) + 1}")
    column_names = unique_column_names(headers)

    records: list[TableRecord] = []
    occurrences: Counter[str] = Counter()
    for row in rows:
        raw_cells = [extract_cell(cell) for cell in row.find_all(("td", "th"), recursive=False)]
        if not raw_cells:
            continue
        values = {
            column_name: raw_cells[index]["value"] if index < len(raw_cells) else None
            for index, column_name in enumerate(column_names)
        }
        value_key = json.dumps(values, ensure_ascii=False, sort_keys=True)
        occurrences[value_key] += 1
        hash_input = json.dumps(
            {"values": values, "occurrence": occurrences[value_key]},
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
        records.append(
            TableRecord(
                values=values,
                cells=raw_cells,
                html=str(row),
                row_hash=hashlib.sha256(hash_input).hexdigest(),
            )
        )

    title_tag = soup.find("title")
    description_tag = soup.find("meta", attrs={"name": "description"})
    return PageData(
        title=clean_text(title_tag.get_text(" ", strip=True)) if title_tag else "",
        description=clean_text(description_tag.get("content", "")) if description_tag else "",
        headers=headers,
        column_names=column_names,
        records=records,
    )


def fetch_page(url: str, timeout: int = DEFAULT_TIMEOUT, user_agent: str = DEFAULT_USER_AGENT) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": user_agent, "Accept-Language": "es-CL,es;q=0.9"},
        timeout=timeout,
    )
    response.raise_for_status()
    response.encoding = response.apparent_encoding or response.encoding
    return response.text


def create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS scrape_runs (
            id INTEGER PRIMARY KEY,
            source_url TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            page_title TEXT NOT NULL,
            page_description TEXT NOT NULL,
            headers_json TEXT NOT NULL,
            row_count INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS source_columns (
            position INTEGER PRIMARY KEY,
            source_name TEXT NOT NULL,
            sqlite_name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY,
            run_id INTEGER NOT NULL REFERENCES scrape_runs(id),
            row_hash TEXT NOT NULL UNIQUE,
            source_url TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            raw_json TEXT NOT NULL,
            row_html TEXT NOT NULL
        );
        """
    )


def ensure_dynamic_columns(connection: sqlite3.Connection, headers: list[str], column_names: list[str]) -> None:
    for position, (header, column_name) in enumerate(zip(headers, column_names), start=1):
        connection.execute(
            "INSERT INTO source_columns(position, source_name, sqlite_name) VALUES (?, ?, ?) "
            "ON CONFLICT(position) DO UPDATE SET source_name=excluded.source_name, sqlite_name=excluded.sqlite_name",
            (position, header, column_name),
        )
        existing = connection.execute(
            "SELECT 1 FROM pragma_table_info('records') WHERE name = ?",
            (column_name,),
        ).fetchone()
        if not existing:
            connection.execute(
                f"ALTER TABLE records ADD COLUMN {quote_identifier(column_name)} TEXT"
            )


def store_page(connection: sqlite3.Connection, page: PageData, source_url: str) -> int:
    """Guarda una extracción completa y devuelve el ID de ejecución."""

    fetched_at = datetime.now(timezone.utc).isoformat()
    with connection:
        create_schema(connection)
        ensure_dynamic_columns(connection, page.headers, page.column_names)
        run_cursor = connection.execute(
            """
            INSERT INTO scrape_runs(
                source_url, fetched_at, page_title, page_description, headers_json, row_count
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                source_url,
                fetched_at,
                page.title,
                page.description,
                json.dumps(page.headers, ensure_ascii=False),
                len(page.records),
            ),
        )
        run_id = int(run_cursor.lastrowid)

        fixed_columns = ["run_id", "row_hash", "source_url", "fetched_at", "raw_json", "row_html"]
        all_columns = fixed_columns + page.column_names
        quoted_columns = ", ".join(quote_identifier(column) for column in all_columns)
        placeholders = ", ".join("?" for _ in all_columns)
        dynamic_assignments = ", ".join(
            f"{quote_identifier(column)} = excluded.{quote_identifier(column)}"
            for column in ["run_id", "source_url", "fetched_at", "raw_json", "row_html", *page.column_names]
        )
        sql = (
            f"INSERT INTO records ({quoted_columns}) VALUES ({placeholders}) "
            f"ON CONFLICT(row_hash) DO UPDATE SET {dynamic_assignments}"
        )
        for record in page.records:
            raw_data = {
                "headers": page.headers,
                "values": record.values,
                "cells": record.cells,
            }
            connection.execute(
                sql,
                [
                    run_id,
                    record.row_hash,
                    source_url,
                    fetched_at,
                    json.dumps(raw_data, ensure_ascii=False),
                    record.html,
                    *record.values.values(),
                ],
            )
    return run_id


def import_page(
    url: str,
    database: str | Path,
    timeout: int = DEFAULT_TIMEOUT,
    table_selector: str | None = None,
    user_agent: str = DEFAULT_USER_AGENT,
) -> tuple[int, int]:
    html = fetch_page(url, timeout=timeout, user_agent=user_agent)
    page = extract_page(html, table_selector=table_selector)
    connection = sqlite3.connect(database)
    try:
        run_id = store_page(connection, page, url)
    finally:
        connection.close()
    return run_id, len(page.records)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="URL de la página a extraer")
    parser.add_argument("--database", default=DEFAULT_DATABASE, help="Archivo SQLite de salida")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout HTTP en segundos")
    parser.add_argument("--table-selector", help="Selector CSS opcional para elegir la tabla")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="User-Agent HTTP")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_id, row_count = import_page(
        url=args.url,
        database=args.database,
        timeout=args.timeout,
        table_selector=args.table_selector,
        user_agent=args.user_agent,
    )
    print(f"Extracción {run_id} completada: {row_count} registros en {args.database}")


if __name__ == "__main__":
    main()
