# serializers.py
from rest_framework import serializers
from .models import Contacto

class ContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacto
        fields = ['id', 'nombre', 'funcion', 'foto', 'telefono', 'junta_vecinos', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_telefono(self, value):
        """Validar formato del teléfono"""
        if not value.isdigit() and not value.startswith('+'):
            raise serializers.ValidationError("El teléfono debe contener solo números o comenzar con +")
        return value
    
    def validate_foto(self, value):
        """Validar que la foto sea una URL válida o base64"""
        if value and not (value.startswith('http') or value.startswith('data:image')):
            raise serializers.ValidationError("La foto debe ser una URL válida o una imagen en base64")
        return value