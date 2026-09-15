from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from core.models import LicenciaMedica


ROLES = {
    "viewer": ("view_licenciamedica",),
    "normal": ("view_licenciamedica", "add_licenciamedica"),
    "admin": (
        "view_licenciamedica",
        "add_licenciamedica",
        "change_licenciamedica",
        "delete_licenciamedica",
    ),
}


class Command(BaseCommand):
    help = "Crea los grupos y permisos de la aplicacion."

    def handle(self, *args, **options):
        content_type = ContentType.objects.get_for_model(LicenciaMedica)
        permisos = Permission.objects.filter(
            content_type=content_type,
            codename__in={permiso for permisos in ROLES.values() for permiso in permisos},
        )
        permisos_por_codigo = {permiso.codename: permiso for permiso in permisos}

        for nombre, codigos in ROLES.items():
            grupo, _ = Group.objects.get_or_create(name=nombre)
            grupo.permissions.set(
                [permisos_por_codigo[codigo] for codigo in codigos]
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Rol {nombre} configurado con {len(codigos)} permiso(s)."
                )
            )
