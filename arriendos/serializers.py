from rest_framework import serializers
from .models import SolicitudArriendo

class SolicitudArriendoSerializer(serializers.ModelSerializer):
    solicitante_nombre = serializers.CharField(source='solicitante.get_full_name', read_only=True)
    
    class Meta:
        model = SolicitudArriendo
        fields = [
            'id', 'solicitante', 'solicitante_nombre', 'fecha_evento', 
            'hora_inicio', 'hora_fin', 'motivo', 'cantidad_asistentes', 
            'estado', 'monto_pago', 'comprobante_pago_base64',
            'fecha_solicitud', 'observaciones'
        ]
        read_only_fields = ['id', 'fecha_solicitud', 'solicitante']

class SolicitudArriendoCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear solicitudes"""
    class Meta:
        model = SolicitudArriendo
        fields = [
            'fecha_evento', 'hora_inicio', 'hora_fin', 
            'motivo', 'cantidad_asistentes'
        ]

class ComprobantePagoSerializer(serializers.ModelSerializer):
    """Serializer específico para subir comprobante de pago en base64"""
    class Meta:
        model = SolicitudArriendo
        fields = ['comprobante_pago_base64']

class AprobacionArriendoSerializer(serializers.Serializer):
    """Serializer para aprobar o rechazar solicitudes"""
    ACCIONES = [
        ('APROBAR', 'Aprobar'),
        ('RECHAZAR', 'Rechazar')
    ]
    
    accion = serializers.ChoiceField(choices=ACCIONES)
    observaciones = serializers.CharField(required=False, allow_blank=True)
    monto_pago = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
