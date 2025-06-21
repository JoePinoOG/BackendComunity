from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from decimal import Decimal

class CertificadoResidencia(models.Model):
    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('PUBLICADO', 'Publicado'),
        ('ARCHIVADO', 'Archivado'),
    ]
    
    # Configuración del certificado
    nombre = models.CharField(
        max_length=100,
        default='Certificado de Residencia',
        editable=False
    )
    
    plantilla = models.FileField(
        upload_to='plantillas/certificado_residencia/',
        validators=[FileExtensionValidator(allowed_extensions=['docx'])],
        help_text="Plantilla DOCX del certificado"
    )
    
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Precio del certificado en CLP"
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PUBLICADO'
    )
    
    campos_requeridos = models.JSONField(
        default=list,
        help_text="Campos del formulario en formato JSON"
    )
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración Certificado"
        verbose_name_plural = "Configuración Certificado"
    
    def __str__(self):
        return f"Certificado de Residencia (${self.precio})"

class SolicitudCertificado(models.Model):
    ESTADO_PAGO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('REEMBOLSADO', 'Reembolsado'),
    ]
    
    ESTADO_DOCUMENTO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('GENERADO', 'Generado'),
        ('ENTREGADO', 'Entregado'),
        ('ANULADO', 'Anulado'),
    ]
    
    # Relaciones
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='solicitudes_certificados'
    )
    
    # Datos del certificado
    datos = models.JSONField(
        default=dict,
        help_text="Datos proporcionados para el certificado"
    )
    
    documento = models.FileField(
        upload_to='certificados_generados/%Y/%m/%d/',
        null=True,
        blank=True
    )

    documento_pdf = models.FileField(upload_to='certificados/pdf/', null=True, blank=True)
    
    # Información de pago
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    
    estado_pago = models.CharField(
        max_length=20,
        choices=ESTADO_PAGO_CHOICES,
        default='PENDIENTE'
    )
    
    codigo_transaccion = models.CharField(
        max_length=100,
        blank=True,
        help_text="Código de transacción de Webpay"
    )
    
    respuesta_webpay = models.JSONField(
        null=True,
        blank=True,
        help_text="Respuesta completa de Webpay"
    )
    
    # Estado del documento
    estado_documento = models.CharField(
        max_length=20,
        choices=ESTADO_DOCUMENTO_CHOICES,
        default='PENDIENTE'
    )
    
    # Fechas importantes
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    fecha_generacion = models.DateTimeField(null=True, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Solicitud de Certificado"
        verbose_name_plural = "Solicitudes de Certificados"
        ordering = ['-fecha_solicitud']
        indexes = [
            models.Index(fields=['estado_pago', 'estado_documento']),
            models.Index(fields=['codigo_transaccion']),
        ]
    
    def __str__(self):
        return f"Certificado #{self.id} - {self.usuario} (${self.monto})"

class TransaccionWebpay(models.Model):
    ESTADO_CHOICES = [
        ('INICIADA', 'Iniciada'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
        ('REVERSADA', 'Reversada'),
    ]
    
    solicitud = models.OneToOneField(
        SolicitudCertificado,
        on_delete=models.PROTECT,
        related_name='transaccion'
    )
    
    token = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    respuesta = models.JSONField()
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Transacción Webpay"
        verbose_name_plural = "Transacciones Webpay"
    
    def __str__(self):
        return f"Transacción {self.token} ({self.get_estado_display()})"