from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea o actualiza el usuario demo con permisos de gestion de licencias."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default="Docente",
            help="Nombre de usuario demo (por defecto: Docente).",
        )
        parser.add_argument(
            "--password",
            required=True,
            help="Clave del usuario demo.",
        )

    def handle(self, *args, **options):
        call_command("crear_roles", verbosity=0)

        user_model = get_user_model()
        usuario, creado = user_model.objects.get_or_create(
            username=options["username"],
        )
        usuario.set_password(options["password"])
        usuario.is_active = True
        usuario.is_staff = False
        usuario.is_superuser = False
        usuario.save()

        grupo_admin = Group.objects.get(name="admin")
        usuario.groups.add(grupo_admin)

        accion = "creado" if creado else "actualizado"
        self.stdout.write(
            self.style.SUCCESS(
                f"Usuario demo '{usuario.username}' {accion} con permisos de gestion."
            )
        )
