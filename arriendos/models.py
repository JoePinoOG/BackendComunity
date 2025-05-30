from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class SolicitudArriendo(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('PAGADO', 'Pagado'),
        ('CANCELADO', 'Cancelado')
    ]
    
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes_arriendo'
    )
    fecha_evento = models.DateTimeField()
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
    comprobante_pago = models.FileField(
        upload_to='comprobantes/',
        null=True,
        blank=True
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_solicitud']
        verbose_name_plural = "Solicitudes de arriendo"

    def __str__(self):
        return f"Solicitud #{self.id} - {self.solicitante.username}"