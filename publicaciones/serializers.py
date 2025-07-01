from rest_framework import serializers
from .models import Publicacion
from usuarios.models import Usuario

class AutorBasicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'first_name', 'last_name', 'rol']

class PublicacionListSerializer(serializers.ModelSerializer):
    autor = AutorBasicoSerializer(read_only=True)
    
    class Meta:
        model = Publicacion
        fields = [
            'id', 'titulo', 'contenido', 'tipo', 'estado', 'imagen',
            'autor', 'fecha_creacion', 'fecha_modificacion', 'fecha_evento',
            'lugar_evento', 'es_destacada', 'fecha_expiracion', 'vistas'
        ]

class PublicacionDetailSerializer(PublicacionListSerializer):
    class Meta(PublicacionListSerializer.Meta):
        fields = PublicacionListSerializer.Meta.fields

class PublicacionCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publicacion
        fields = [
            'titulo', 'contenido', 'tipo', 'imagen', 'fecha_evento', 'lugar_evento'
        ]
    
    def validate_imagen(self, value):
        """Validar que la imagen sea una URL válida o base64"""
        if value and not (value.startswith('http') or value.startswith('data:image')):
            raise serializers.ValidationError("La imagen debe ser una URL válida o una imagen en base64")
        return value
