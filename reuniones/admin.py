from django.contrib import admin
from .models import Reunion

@admin.register(Reunion)
class ReunionAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'fecha', 'lugar', 'motivo')
    list_filter = ('motivo', 'fecha')
    search_fields = ('titulo', 'lugar')