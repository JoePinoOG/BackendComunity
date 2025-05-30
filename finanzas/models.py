from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Transaccion(models.Model):
    TIPO_CHOICES = [
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso')
    ]
    
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    descripcion = models.TextField()
    fecha = models.DateField()
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    comprobante = models.FileField(
        upload_to='comprobantes/',
        null=True,
        blank=True
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Transacciones"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.tipo} ${self.monto} - {self.fecha}"

class CuentaPendiente(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADA', 'Pagada'),
        ('VENCIDA', 'Vencida')
    ]
    
    nombre = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_vencimiento = models.DateField()
    estado = models.CharField(
        max_length=9,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )
    proveedor = models.CharField(max_length=100)
    enlace_pago = models.URLField(blank=True)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.proveedor}"