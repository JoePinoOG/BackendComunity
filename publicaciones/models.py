from django.db import models
from django.conf import settings
from django.utils import timezone

class Publicacion(models.Model):
    TIPOS = [
        ('ANUNCIO', 'Anuncio General'),
        ('EVENTO', 'Evento'),
        ('AVISO', 'Aviso Importante'),
        ('NOTICIA', 'Noticia'),
        ('PERDIDO', 'Objeto Perdido'),
        ('VENTA', 'Venta/Intercambio'),
    ]
    
    ESTADOS = [
        ('ACTIVA', 'Activa'),
        ('PAUSADA', 'Pausada'),
        ('ARCHIVADA', 'Archivada'),
    ]
    
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS, default='ANUNCIO')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVA')
    
    # Imagen opcional - almacenada como base64 o URL
    imagen = models.TextField(
        null=True, 
        blank=True,
        help_text="Imagen para la publicación en formato base64 o URL (opcional)"
    )
    
    # Metadatos
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='publicaciones'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    # Para eventos - campos opcionales
    fecha_evento = models.DateTimeField(null=True, blank=True)
    lugar_evento = models.CharField(max_length=200, null=True, blank=True)
    
    # Configuración de visibilidad
    es_destacada = models.BooleanField(default=False)
    fecha_expiracion = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha después de la cual la publicación se archiva automáticamente"
    )
    
    # Engagement
    vistas = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Publicaciones"
        ordering = ['-es_destacada', '-fecha_creacion']
        
    def __str__(self):
        return f"{self.titulo} - {self.get_tipo_display()}"
    
    def esta_vigente(self):
        """Verifica si la publicación está vigente"""
        if self.estado != 'ACTIVA':
            return False
        if self.fecha_expiracion and self.fecha_expiracion < timezone.now():
            return False
        return True
    
    def incrementar_vistas(self):
        """Incrementa el contador de vistas"""
        self.vistas += 1
        self.save(update_fields=['vistas'])
