# Generated by Django 5.2 on 2025-06-30 17:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reuniones', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reunion',
            name='participantes',
        ),
    ]
