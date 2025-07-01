from django.contrib import admin
from .models import Usuario, HistorialValidacion

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'estado', 'is_active', 'date_joined')
    list_filter = ('estado', 'rol', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'rut')
    actions = ['aprobar_usuarios', 'rechazar_usuarios']
    readonly_fields = ('date_joined', 'last_login')

    def aprobar_usuarios(self, request, queryset):
        queryset.update(estado='APROBADO')
    aprobar_usuarios.short_description = "Aprobar usuarios seleccionados"

    def rechazar_usuarios(self, request, queryset):
        queryset.update(estado='RECHAZADO')
    rechazar_usuarios.short_description = "Rechazar usuarios seleccionados"

@admin.register(HistorialValidacion)
class HistorialValidacionAdmin(admin.ModelAdmin):
    list_display = ('usuario_validado', 'validado_por', 'accion', 'fecha_validacion')
    list_filter = ('accion', 'fecha_validacion')
    search_fields = ('usuario_validado__username', 'validado_por__username')
    readonly_fields = ('fecha_validacion',)
    
    def has_add_permission(self, request):
        # No permitir agregar registros manualmente
        return False
    
    def has_change_permission(self, request, obj=None):
        # No permitir editar registros
        return False