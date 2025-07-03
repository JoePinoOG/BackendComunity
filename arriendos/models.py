from django.db import models
from django.conf import settings

class SolicitudArriendo(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('PAGADO', 'Pagado'),
        ('CANCELADO', 'Cancelado')
    ]
    
    # Datos básicos del solicitante
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes_arriendo'
    )
    
    # Datos del evento
    fecha_evento = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    motivo = models.TextField()
    cantidad_asistentes = models.PositiveIntegerField()
    
    # Estado y pago
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='PENDIENTE'
    )
    monto_pago = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Comprobante como base64
    comprobante_pago_base64 = models.TextField(
        null=True,
        blank=True,
        help_text="Imagen del comprobante en formato base64"
    )
    
    # Fechas
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_solicitud']
        verbose_name_plural = "Solicitudes de arriendo"

    def __str__(self):
        return f"Solicitud #{self.id} - {self.solicitante.username}"