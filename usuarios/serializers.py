from rest_framework import serializers
from .models import Usuario
from django.contrib.auth.hashers import make_password

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'password',
            'first_name', 'last_name', 'rol',
            'direccion', 'telefono', 'rut', 'estado'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'estado': {'read_only': True}  # Solo cambia via aprobación
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

#class AprobarUsuarioSerializer(serializers.Serializer):
 #   estado = serializers.ChoiceField(choices=Usuario.ESTADOS)
  #  observacion = serializers.CharField(required=False)