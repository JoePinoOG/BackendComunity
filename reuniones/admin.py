from django.contrib import admin
from .models import Reunion, Acta

@admin.register(Reunion)
class ReunionAdmin(admin.ModelAdmin):
    list_display = ('motivo', 'fecha', 'lugar', 'convocante')
    search_fields = ('motivo', 'lugar')
    list_filter = ('fecha', 'convocante')

@admin.register(Acta)
class ActaAdmin(admin.ModelAdmin):
    list_display = ('reunion', 'estado', 'creado_por')
    list_filter = ('estado', 'firmado_presidente', 'firmado_secretario')