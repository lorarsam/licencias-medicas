import sqlite3
import tempfile
import unittest
from pathlib import Path

from scraper_suseso import extract_page, store_page


HTML = """
<!doctype html>
<html lang="es">
  <head>
    <title>Registro de sanciones</title>
    <meta name="description" content="Descripción pública">
  </head>
  <body>
    <table>
      <thead><tr><th>RUN Profesional Emisor</th><th>Fecha de resolución</th><th>Detalle</th></tr></thead>
      <tbody>
        <tr><td>11-1</td><td>01/01/2026</td><td><a href="/documento.pdf">Oficio</a></td></tr>
        <tr><td>22-2</td><td>02/01/2026</td><td>Otra sanción</td></tr>
      </tbody>
    </table>
  </body>
</html>
"""


class ScraperSusesoTests(unittest.TestCase):
    def test_extracts_headers_values_and_links_without_hardcoded_rows(self):
        page = extract_page(HTML)

        self.assertEqual(page.headers, ["RUN Profesional Emisor", "Fecha de resolución", "Detalle"])
        self.assertEqual(page.column_names, ["run_profesional_emisor", "fecha_de_resolucion", "detalle"])
        self.assertEqual(len(page.records), 2)
        self.assertEqual(page.records[0].values["run_profesional_emisor"], "11-1")
        self.assertEqual(page.records[0].cells[2]["links"][0]["href"], "/documento.pdf")

    def test_store_is_idempotent_for_the_same_extraction(self):
        page = extract_page(HTML)
        with tempfile.TemporaryDirectory() as temporary_directory:
            database = Path(temporary_directory) / "test.sqlite3"
            connection = sqlite3.connect(database)
            try:
                store_page(connection, page, "https://example.test/registro")
                store_page(connection, page, "https://example.test/registro")
                records = connection.execute("SELECT COUNT(*) FROM records").fetchone()[0]
                runs = connection.execute("SELECT COUNT(*) FROM scrape_runs").fetchone()[0]
                value = connection.execute(
                    "SELECT fecha_de_resolucion FROM records WHERE run_profesional_emisor = ?",
                    ("11-1",),
                ).fetchone()[0]
            finally:
                connection.close()

        self.assertEqual(records, 2)
        self.assertEqual(runs, 2)
        self.assertEqual(value, "01/01/2026")


if __name__ == "__main__":
    unittest.main()
