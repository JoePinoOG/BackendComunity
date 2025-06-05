from django.db import models
from django.conf import settings 

class JuntaVecinos(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    sector = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class SedeComunitaria(models.Model):
    junta = models.OneToOneField('JuntaVecinos', on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255)
    capacidad = models.IntegerField()
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Sede de {self.junta.nombre}"

class Anuncio(models.Model):
    junta = models.ForeignKey('JuntaVecinos', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    contenido = models.TextField()
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True
    )
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("publicar_anuncio", "Puede publicar anuncios"),
        ]

    def __str__(self):
        return self.titulo

class ContactoAutoridad(models.Model):
    TIPO_CHOICES = [
        ('emergencia', 'Emergencia'),
        ('municipal', 'Municipalidad'),
        ('empresa', 'Empresa'),
        ('otro', 'Otro'),
    ]

    junta = models.ForeignKey('JuntaVecinos', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    cargo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(blank=True, null=True)
    visible_para_vecinos = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} ({self.cargo})"

# Create your models here.
