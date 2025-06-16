from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.response import Response
from rest_framework import status

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)  # O usa logging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        direccion = serializer.validated_data.get('direccion')
        try:
            juntas_vecinos = asignar_junta_vecinos(direccion)  # Asegúrate de que esta función existe y funciona
        except Exception as e:
            print(str(e))
            return Response({'error': 'Error al asignar junta de vecinos'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(juntas_vecinos=juntas_vecinos, estado='PENDIENTE')
        return Response(serializer.data, status=status.HTTP_201_CREATED)