# admin.py
from django.contrib import admin
from .models import Contacto

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'funcion', 'telefono', 'junta_vecinos', 'created_at']
    list_filter = ['funcion', 'junta_vecinos', 'created_at']
    search_fields = ['nombre', 'funcion', 'telefono']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'funcion', 'telefono')
        }),
        ('Imagen', {
            'fields': ('foto',)
        }),
        ('Asociación', {
            'fields': ('junta_vecinos',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )