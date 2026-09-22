from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0002_alter_licenciamedica_estado_medicosancionado"),
    ]

    operations = [
        migrations.AddField(
            model_name="licenciamedica",
            name="creado_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="licencias_creadas",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
