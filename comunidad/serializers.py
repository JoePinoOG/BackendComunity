from rest_framework import serializers
from .models import JuntaVecinos, SedeComunitaria, Anuncio, ContactoAutoridad

# Serializer para Junta de Vecinos
class JuntaVecinosSerializer(serializers.ModelSerializer):
    class Meta:
        model = JuntaVecinos
        fields = '__all__'

# Serializer para Sede Comunitaria
class SedeComunitariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SedeComunitaria
        fields = '__all__'

# Serializer para Anuncio
class AnuncioSerializer(serializers.ModelSerializer):
    creado_por = serializers.StringRelatedField()  # Opcional: mostrar el nombre del usuario que creó el anuncio

    class Meta:
        model = Anuncio
        fields = '__all__'

# Serializer para Contactos de Autoridades
class ContactoAutoridadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactoAutoridad
        fields = '__all__'
