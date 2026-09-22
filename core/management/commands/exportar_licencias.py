import json
from pathlib import Path

from django.core.management.base import BaseCommand

from core.models import LicenciaMedica


def serializar_licencia(licencia):
    return {
        "id": licencia.pk,
        "medico": licencia.medico,
        "rut_medico": licencia.rut_medico,
        "funcionario": licencia.funcionario,
        "rut_funcionario": licencia.rut_funcionario,
        "dias_reposo": licencia.dias_reposo,
        "fecha_emision": licencia.fecha_emision.isoformat(),
        "tipo_licencia": licencia.tipo_licencia,
        "estado": licencia.estado,
        "motivo": licencia.motivo,
        "fecha": licencia.fecha.isoformat(),
        "eliminado": licencia.eliminado,
        "fecha_eliminacion": (
            licencia.fecha_eliminacion.isoformat()
            if licencia.fecha_eliminacion
            else None
        ),
        "creado_por": licencia.creado_por.username if licencia.creado_por else None,
    }


class Command(BaseCommand):
    help = "Exporta licencias sin incluir contrasenas ni sesiones de usuarios."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="licencias_respaldo.json",
            help="Ruta del archivo de respaldo.",
        )

    def handle(self, *args, **options):
        target = Path(options["path"])
        registros = [
            serializar_licencia(licencia)
            for licencia in LicenciaMedica.objects.select_related("creado_por")
        ]
        contenido = {"version": 1, "registros": registros}
        target.write_text(
            json.dumps(contenido, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Exportacion completada: {len(registros)} licencia(s) en {target}."
            )
        )
