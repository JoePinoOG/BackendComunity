# Generated by Django 5.2 on 2025-06-29 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitudcertificado',
            name='documento_pdf',
            field=models.FileField(blank=True, null=True, upload_to='certificados/pdf/'),
        ),
    ]
