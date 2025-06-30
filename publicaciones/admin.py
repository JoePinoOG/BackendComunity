from django.contrib import admin
from .models import Publicacion

@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'tipo', 'autor', 'estado', 
        'fecha_creacion', 'vistas'
    ]
    list_filter = ['tipo', 'estado', 'fecha_creacion', 'autor__rol']
    search_fields = ['titulo', 'contenido', 'autor__username']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion', 'vistas']
    date_hierarchy = 'fecha_creacion'
    
    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'contenido', 'tipo', 'estado', 'imagen')
        }),
        ('Metadatos', {
            'fields': ('autor', 'fecha_creacion', 'fecha_modificacion', 'vistas')
        }),
    )
