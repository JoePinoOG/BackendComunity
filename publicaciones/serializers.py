from rest_framework import serializers
from .models import Publicacion
from usuarios.models import Usuario

class AutorBasicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'first_name', 'last_name', 'rol']

class PublicacionListSerializer(serializers.ModelSerializer):
    autor = AutorBasicoSerializer(read_only=True)
    imagen_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Publicacion
        fields = [
            'id', 'titulo', 'contenido', 'tipo', 'estado', 'imagen_url',
            'autor', 'fecha_creacion', 'fecha_modificacion', 'fecha_evento',
            'lugar_evento', 'es_destacada', 'fecha_expiracion', 'vistas'
        ]
    
    def get_imagen_url(self, obj):
        if obj.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen.url)
        return None

class PublicacionDetailSerializer(PublicacionListSerializer):
    class Meta(PublicacionListSerializer.Meta):
        fields = PublicacionListSerializer.Meta.fields

class PublicacionCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publicacion
        fields = [
            'titulo', 'contenido', 'tipo', 'imagen'
        ]
