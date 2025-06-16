from django.contrib import admin
# Register your models here.
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'estado', 'is_active')
    list_filter = ('estado', 'rol')
    actions = ['aprobar_usuarios', 'rechazar_usuarios']

    def aprobar_usuarios(self, request, queryset):
        queryset.update(estado='APROBADO')
    aprobar_usuarios.short_description = "Aprobar usuarios seleccionados"

    def rechazar_usuarios(self, request, queryset):
        queryset.update(estado='RECHAZADO')
    rechazar_usuarios.short_description = "Rechazar usuarios seleccionados"