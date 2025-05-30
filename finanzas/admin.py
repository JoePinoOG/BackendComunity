from django.contrib import admin
from .models import Transaccion, CuentaPendiente

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'monto', 'fecha', 'creado_por')
    list_filter = ('tipo', 'fecha')
    search_fields = ('descripcion',)

@admin.register(CuentaPendiente)
class CuentaPendienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'monto', 'fecha_vencimiento', 'estado')
    list_filter = ('estado', 'fecha_vencimiento')