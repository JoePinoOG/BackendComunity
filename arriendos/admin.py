from django.contrib import admin
from .models import SolicitudArriendo

@admin.register(SolicitudArriendo)
class SolicitudArriendoAdmin(admin.ModelAdmin):
    list_display = ('id', 'solicitante', 'fecha_evento', 'estado')
    list_filter = ('estado', 'fecha_evento')
    search_fields = ('solicitante__username', 'motivo')