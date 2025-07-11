# Generated by Django 5.2 on 2025-06-30 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentos', '0002_solicitudcertificado_documento_pdf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificadoresidencia',
            name='campos_requeridos',
            field=models.TextField(default='[]', help_text='Campos del formulario en formato JSON'),
        ),
        migrations.AlterField(
            model_name='solicitudcertificado',
            name='datos',
            field=models.TextField(default='{}', help_text='Datos proporcionados para el certificado'),
        ),
        migrations.AlterField(
            model_name='solicitudcertificado',
            name='respuesta_webpay',
            field=models.TextField(blank=True, help_text='Respuesta completa de Webpay', null=True),
        ),
        migrations.AlterField(
            model_name='transaccionwebpay',
            name='respuesta',
            field=models.TextField(),
        ),
    ]
