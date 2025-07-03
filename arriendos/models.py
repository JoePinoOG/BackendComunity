from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time

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
    motivo = models.TextField(max_length=500)
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
    observaciones = models.TextField(blank=True, max_length=500)

    class Meta:
        ordering = ['-fecha_solicitud']
        verbose_name_plural = "Solicitudes de arriendo"
        # Índices para mejorar performance
        indexes = [
            models.Index(fields=['fecha_evento', 'estado']),
            models.Index(fields=['solicitante', 'estado']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f"Solicitud #{self.id} - {self.solicitante.username} - {self.fecha_evento}"
    
    def clean(self):
        """Validaciones a nivel de modelo"""
        super().clean()
        
        # Validar que la fecha no sea en el pasado
        if self.fecha_evento and self.fecha_evento < timezone.now().date():
            raise ValidationError({
                'fecha_evento': 'No se pueden crear solicitudes para fechas pasadas.'
            })
        
        # Validar horarios
        if self.hora_inicio and self.hora_fin:
            if self.hora_inicio >= self.hora_fin:
                raise ValidationError({
                    'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio.'
                })
            
            # Validar horario de funcionamiento
            hora_apertura = time(8, 0)
            hora_cierre = time(22, 0)
            
            if self.hora_inicio < hora_apertura or self.hora_fin > hora_cierre:
                raise ValidationError({
                    'hora_inicio': f'El salón funciona de {hora_apertura.strftime("%H:%M")} a {hora_cierre.strftime("%H:%M")}.'
                })
        
        # Validar capacidad
        if self.cantidad_asistentes and self.cantidad_asistentes > 100:
            raise ValidationError({
                'cantidad_asistentes': 'La capacidad máxima del salón es de 100 personas.'
            })
    
    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def duracion_horas(self):
        """Calcula la duración del evento en horas"""
        if self.hora_inicio and self.hora_fin:
            inicio = datetime.combine(datetime.today(), self.hora_inicio)
            fin = datetime.combine(datetime.today(), self.hora_fin)
            duracion = fin - inicio
            return duracion.total_seconds() / 3600
        return 0
    
    @property
    def esta_pagado(self):
        """Verifica si la solicitud está pagada"""
        return self.estado == 'PAGADO'
    
    @property
    def esta_aprobado(self):
        """Verifica si la solicitud está aprobada o pagada"""
        return self.estado in ['APROBADO', 'PAGADO']
    
    @property
    def puede_cancelar(self):
        """Verifica si la solicitud puede ser cancelada"""
        return self.estado in ['PENDIENTE', 'APROBADO']
    
    @property
    def tiene_comprobante(self):
        """Verifica si tiene comprobante de pago"""
        return bool(self.comprobante_pago_base64)
    
    def aprobar(self, monto_pago, observaciones=''):
        """Método para aprobar la solicitud"""
        if self.estado != 'PENDIENTE':
            raise ValueError("Solo se pueden aprobar solicitudes pendientes.")
        
        self.estado = 'APROBADO'
        self.monto_pago = monto_pago
        if observaciones:
            self.observaciones = observaciones
        self.save()
    
    def rechazar(self, observaciones):
        """Método para rechazar la solicitud"""
        if self.estado != 'PENDIENTE':
            raise ValueError("Solo se pueden rechazar solicitudes pendientes.")
        
        self.estado = 'CANCELADO'
        self.observaciones = observaciones
        self.save()
    
    def marcar_pagado(self):
        """Método para marcar como pagado"""
        if self.estado != 'APROBADO':
            raise ValueError("Solo se pueden marcar como pagadas las solicitudes aprobadas.")
        
        self.estado = 'PAGADO'
        self.save()