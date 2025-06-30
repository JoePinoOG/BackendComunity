# models.py
from django.db import models
from django.contrib.auth.models import User

class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    funcion = models.CharField(max_length=100)
    foto = models.TextField(blank=True, null=True)  # Para almacenar base64 o URL
    telefono = models.CharField(max_length=20)
    junta_vecinos = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.funcion}"