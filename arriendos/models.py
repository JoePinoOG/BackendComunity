from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class SolicitudArriendo(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('PAGADO', 'Pagado'),
        ('CANCELADO', 'Cancelado')
    ]
    
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes_arriendo'
    )
    fecha_evento = models.DateField()  # Solo la fecha del evento
    hora_inicio = models.TimeField(null=True, blank=True)   # Hora de inicio del arriendo
    hora_fin = models.TimeField(null=True, blank=True)      # Hora de término del arriendo
    motivo = models.TextField()
    cantidad_asistentes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
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
    comprobante_pago = models.ImageField(
        upload_to='comprobantes_arriendo/',
        null=True,
        blank=True,
        help_text="Imagen del comprobante de pago del arriendo"
    )
    
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)
    token_webpay = models.CharField(max_length=100, blank=True, null=True)  # Para asociar el pago Webpay

    class Meta:
        ordering = ['-fecha_solicitud']
        verbose_name_plural = "Solicitudes de arriendo"
        unique_together = ('fecha_evento', 'hora_inicio', 'hora_fin')  # No se puede repetir el mismo bloque

    def __str__(self):
        return f"Solicitud #{self.id} - {self.solicitante.username}"