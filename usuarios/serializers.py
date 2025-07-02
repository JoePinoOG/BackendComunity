from rest_framework import serializers
from .models import Usuario
from django.contrib.auth.hashers import make_password
from django.utils import timezone

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'password',
            'first_name', 'last_name', 'rol',
            'direccion', 'telefono', 'rut', 'estado',
            'date_joined', 'last_login'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'estado': {'read_only': True},  # Solo cambia via aprobación
            'date_joined': {'read_only': True},
            'last_login': {'read_only': True}
        }

    def create(self, validated_data):
        # Si el rol es de directiva, el estado debe ser PENDIENTE
        if validated_data.get('rol') in ['SECRETARIO', 'TESORERO', 'PRESIDENTE']:
            validated_data['estado'] = 'PENDIENTE'
        else:
            # Los vecinos se aprueban automáticamente
            validated_data['estado'] = 'APROBADO'
            
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class UsuarioValidacionSerializer(serializers.ModelSerializer):
    """Serializer para mostrar usuarios pendientes de validación"""
    tiempo_pendiente = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'rol', 'direccion', 'telefono', 'rut', 'estado', 
            'date_joined', 'tiempo_pendiente'
        ]
    
    def get_tiempo_pendiente(self, obj):
        """Calcular tiempo que lleva pendiente"""
        if obj.estado == 'PENDIENTE':
            tiempo = timezone.now() - obj.date_joined
            dias = tiempo.days
            if dias == 0:
                return "Hoy"
            elif dias == 1:
                return "1 día"
            else:
                return f"{dias} días"
        return None

class ValidarUsuarioSerializer(serializers.Serializer):
    """Serializer para validar/rechazar usuarios"""
    ACCIONES = [
        ('APROBAR', 'Aprobar'),
        ('RECHAZAR', 'Rechazar'),
    ]
    
    accion = serializers.ChoiceField(choices=ACCIONES)
    observacion = serializers.CharField(
        required=False, 
        max_length=500,
        help_text="Motivo de aprobación o rechazo (opcional)"
    )
    
    def validate_accion(self, value):
        if value not in ['APROBAR', 'RECHAZAR']:
            raise serializers.ValidationError("La acción debe ser APROBAR o RECHAZAR")
        return value

class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """Serializer específico para registro de usuarios"""
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'rol',
            'direccion', 'telefono', 'rut'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def validate(self, data):
        # Verificar que las contraseñas coincidan
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        
        # Verificar que el RUT no exista
        if Usuario.objects.filter(rut=data['rut']).exists():
            raise serializers.ValidationError("Ya existe un usuario con este RUT")
        
        return data
    
    def create(self, validated_data):
        # Remover password_confirm antes de crear
        validated_data.pop('password_confirm', None)
        
        # Si el rol es de directiva, el estado debe ser PENDIENTE
        if validated_data.get('rol') in ['SECRETARIO', 'TESORERO', 'PRESIDENTE']:
            validated_data['estado'] = 'PENDIENTE'
        else:
            # Los vecinos se aprueban automáticamente
            validated_data['estado'] = 'APROBADO'
            
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)