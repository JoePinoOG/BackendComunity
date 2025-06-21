from rest_framework import serializers
from .models import CertificadoResidencia, SolicitudCertificado, TransaccionWebpay
from django.conf import settings
import os

class CertificadoResidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificadoResidencia
        fields = ['id', 'nombre', 'precio', 'campos_requeridos']
        read_only_fields = ['id', 'nombre']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Asegúrate que campos_requeridos sea un dict/lista válido
        if isinstance(instance.campos_requeridos, str):
            representation['campos_requeridos'] = json.loads(instance.campos_requeridos)
        return representation

class SolicitudCertificadoSerializer(serializers.ModelSerializer):
    estado_pago_display = serializers.CharField(source='get_estado_pago_display', read_only=True)
    estado_documento_display = serializers.CharField(source='get_estado_documento_display', read_only=True)
    documento_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudCertificado
        fields = [
            'id', 
            'usuario', 
            'datos', 
            'monto', 
            'estado_pago', 
            'estado_pago_display',
            'estado_documento',
            'estado_documento_display',
            'documento',
            'documento_url',
            'fecha_solicitud',
            'fecha_generacion',
            'fecha_entrega'
        ]
        read_only_fields = [
            'id', 
            'usuario', 
            'monto', 
            'estado_pago', 
            'estado_documento',
            'documento',
            'fecha_solicitud',
            'fecha_generacion',
            'fecha_entrega'
        ]
    
    def get_documento_url(self, obj):
        if obj.documento:
            return os.path.join(settings.MEDIA_URL, obj.documento.name)
        return None

    def validate_datos(self, value):
        """Valida que los datos incluyan todos los campos requeridos"""
        config = CertificadoResidencia.objects.first()
        if not config:
            raise serializers.ValidationError("Configuración no disponible")
        
        campos_requeridos = config.campos_requeridos if isinstance(config.campos_requeridos, list) else json.loads(config.campos_requeridos)
        
        for campo in campos_requeridos:
            if campo['requerido'] and campo['nombre'] not in value:
                raise serializers.ValidationError(f"Falta el campo requerido: {campo['nombre']}")
        
        return value

class TransaccionWebpaySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransaccionWebpay
        fields = ['token', 'estado', 'fecha_creacion', 'fecha_actualizacion']
        read_only_fields = fields

class IniciarPagoSerializer(serializers.Serializer):
    url_redirect = serializers.URLField()
    token = serializers.CharField()
    
    def create(self, validated_data):
        raise NotImplementedError()
    
    def update(self, instance, validated_data):
        raise NotImplementedError()

# Serializer para la solicitud inicial
class SolicitudInicialSerializer(serializers.Serializer):
    nombre_completo = serializers.CharField(max_length=200)
    cedula_identidad = serializers.CharField(max_length=20)
    domicilio_completo = serializers.CharField(max_length=300)
    institucion_destino = serializers.CharField(max_length=200, required=False, allow_blank=True)
    
    def create(self, validated_data):
        config = CertificadoResidencia.objects.first()
        usuario = self.context['request'].user
        
        solicitud = SolicitudCertificado.objects.create(
            usuario=usuario,
            datos=validated_data,
            monto=config.precio
        )
        
        return solicitud

# Serializer para la respuesta de Webpay
class WebpayResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    url = serializers.URLField()
    
    def create(self, validated_data):
        raise NotImplementedError()
    
    def update(self, instance, validated_data):
        raise NotImplementedError()