# Scraper SUSESO

El script `scraper_suseso.py` extrae la tabla pública de sanciones de SUSESO y
la guarda en `suseso.sqlite3`. La base es independiente de la base SQLite de
Django (`db.sqlite3`).

## Instalación

```text
python -m pip install -r requirements.txt
```

## Ejecución

```text
python scraper_suseso.py
```

Opciones disponibles:

```text
python scraper_suseso.py --url URL --database archivo.sqlite3 --timeout 60
```

Si la página cambia y contiene varias tablas, se puede indicar cuál procesar:

```text
python scraper_suseso.py --table-selector "table#tabla_sancionesLM"
```

## Estructura de datos

- `scrape_runs`: historial de ejecuciones, URL, título, descripción y encabezados.
- `source_columns`: relación entre los encabezados originales y los nombres SQLite.
- `records`: filas extraídas y columnas creadas dinámicamente desde el HTML.
- `raw_json` conserva encabezados, valores, enlaces y HTML de cada fila.

Las filas se identifican mediante un hash de sus valores. Ejecutar nuevamente el
script no duplica una fila idéntica; sí conserva una nueva versión si cambia su
contenido.
