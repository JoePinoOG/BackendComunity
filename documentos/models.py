from django.db import models
from django.conf import settings

class PlantillaDocumento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='plantillas/')
    tipo = models.CharField(max_length=50, choices=[
        ('certificado', 'Certificado'),
        ('solicitud', 'Solicitud'),
        ('constancia', 'Constancia'),
    ])
    campos_requeridos = models.JSONField(
        help_text="Campos que deben ser rellenados en la plantilla (formato JSON)",
        default=dict
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

class SolicitudDocumento(models.Model):
    plantilla = models.ForeignKey(PlantillaDocumento, on_delete=models.CASCADE)
    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    datos_documento = models.JSONField(
        help_text="Datos para rellenar la plantilla (formato JSON)"
    )
    documento_generado = models.FileField(upload_to='documentos_generados/', null=True, blank=True)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('generado', 'Generado'),
        ('entregado', 'Entregado'),
        ('rechazado', 'Rechazado'),
    ], default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_generacion = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Solicitud de {self.plantilla.nombre} por {self.solicitante.username}"
