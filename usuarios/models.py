from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    ROLES = (
        ('VECINO', 'Vecino'),
        ('SECRETARIO', 'Secretario'),
        ('TESORERO', 'Tesorero'),
        ('PRESIDENTE', 'Presidente'),
    )
    ESTADOS = (
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    )
    
    rol = models.CharField(max_length=20, choices=ROLES, default='VECINO')
    direccion = models.CharField(max_length=200, default='Dirección no especificada', blank=True)
    telefono = models.CharField(max_length=15, default='Telefono no Especificado', blank=True)
    rut = models.CharField(max_length=12, unique=True, default='Rut no especificado', blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    juntas_vecinos = models.ForeignKey(
        'comunidad.JuntaVecinos',  # Asume que existe este modelo
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.get_full_name()} ({self.rol})"