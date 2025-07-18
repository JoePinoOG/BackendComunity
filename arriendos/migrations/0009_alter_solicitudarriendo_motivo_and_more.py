# Generated by Django 5.2 on 2025-07-03 23:49

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arriendos', '0008_alter_solicitudarriendo_cantidad_asistentes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitudarriendo',
            name='motivo',
            field=models.TextField(max_length=500),
        ),
        migrations.AlterField(
            model_name='solicitudarriendo',
            name='observaciones',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AddIndex(
            model_name='solicitudarriendo',
            index=models.Index(fields=['fecha_evento', 'estado'], name='arriendos_s_fecha_e_fef668_idx'),
        ),
        migrations.AddIndex(
            model_name='solicitudarriendo',
            index=models.Index(fields=['solicitante', 'estado'], name='arriendos_s_solicit_0b8261_idx'),
        ),
        migrations.AddIndex(
            model_name='solicitudarriendo',
            index=models.Index(fields=['estado'], name='arriendos_s_estado_40906a_idx'),
        ),
    ]
