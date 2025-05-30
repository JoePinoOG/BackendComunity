from django.db import models
from django.conf import settings
from django.utils import timezone

class Reunion(models.Model):
    MOTIVOS = [
        ('ORDINARIA', 'Ordinaria'),
        ('EXTRAORDINARIA', 'Extraordinaria'),
        ('EMERGENCIA', 'Emergencia')
    ]
    
    motivo = models.CharField(max_length=50, choices=MOTIVOS, null=True, blank=True)
    fecha = models.DateTimeField()
    lugar = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    convocante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reuniones_convocadas',
        null=True, 
        blank=True
    )
    participantes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='reuniones_participantes'
    )
    creada_en = models.DateTimeField(auto_now_add=True,null=True, blank=True)

    class Meta:
        verbose_name_plural = "Reuniones"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_motivo_display()} - {self.fecha.strftime('%d/%m/%Y')}"

class Acta(models.Model):
    ESTADOS = [
        ('BORRADOR', 'Borrador'),
        ('PENDIENTE', 'Pendiente de validación'),
        ('VALIDADA', 'Validada')
    ]
    
    reunion = models.OneToOneField(
        Reunion,
        on_delete=models.CASCADE,
        related_name='acta',
        null=True, blank=True
    )
    contenido = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='BORRADOR')
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='actas_creadas',
        null=True, blank=True
    )
    firmado_presidente = models.BooleanField(default=False)
    firmado_secretario = models.BooleanField(default=False)
    ultima_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Acta #{self.id} - {self.reunion}"