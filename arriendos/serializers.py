from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, time
from .models import SolicitudArriendo

class SolicitudArriendoSerializer(serializers.ModelSerializer):
    solicitante_nombre = serializers.CharField(source='solicitante.get_full_name', read_only=True)
    tiene_comprobante = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudArriendo
        fields = [
            'id', 'solicitante', 'solicitante_nombre', 'fecha_evento', 
            'hora_inicio', 'hora_fin', 'motivo', 'cantidad_asistentes', 
            'estado', 'monto_pago', 'comprobante_pago_base64',
            'fecha_solicitud', 'observaciones', 'tiene_comprobante'
        ]
        read_only_fields = ['id', 'fecha_solicitud', 'solicitante']
    
    def get_tiene_comprobante(self, obj):
        """Indica si la solicitud tiene comprobante de pago"""
        return bool(obj.comprobante_pago_base64)

class SolicitudArriendoCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear solicitudes"""
    
    class Meta:
        model = SolicitudArriendo
        fields = [
            'fecha_evento', 'hora_inicio', 'hora_fin', 
            'motivo', 'cantidad_asistentes'
        ]
    
    def validate_fecha_evento(self, value):
        """Validar que la fecha del evento no sea en el pasado"""
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "No se pueden crear solicitudes para fechas pasadas."
            )
        return value
    
    def validate(self, data):
        """Validaciones cruzadas"""
        hora_inicio = data.get('hora_inicio')
        hora_fin = data.get('hora_fin')
        
        if hora_inicio and hora_fin:
            if hora_inicio >= hora_fin:
                raise serializers.ValidationError({
                    'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio.'
                })
            
            # Validar horario de funcionamiento (ej: 8:00 - 22:00)
            hora_apertura = time(8, 0)  # 8:00 AM
            hora_cierre = time(22, 0)   # 10:00 PM
            
            if hora_inicio < hora_apertura or hora_fin > hora_cierre:
                raise serializers.ValidationError({
                    'hora_inicio': f'El salón está disponible de {hora_apertura.strftime("%H:%M")} a {hora_cierre.strftime("%H:%M")}.'
                })
        
        cantidad_asistentes = data.get('cantidad_asistentes')
        if cantidad_asistentes and cantidad_asistentes > 100:  # Capacidad máxima ejemplo
            raise serializers.ValidationError({
                'cantidad_asistentes': 'La capacidad máxima del salón es de 100 personas.'
            })
        
        return data

class ComprobantePagoSerializer(serializers.ModelSerializer):
    """Serializer específico para subir comprobante de pago en base64"""
    
    class Meta:
        model = SolicitudArriendo
        fields = ['comprobante_pago_base64']
    
    def validate_comprobante_pago_base64(self, value):
        """Validar formato base64 de imagen"""
        if not value:
            raise serializers.ValidationError("El comprobante de pago es obligatorio.")
        
        # Verificar que sea un formato base64 válido
        if not value.startswith('data:image/'):
            raise serializers.ValidationError(
                "El comprobante debe ser una imagen en formato base64 válido."
            )
        
        # Verificar tamaño aproximado (base64 es ~33% más grande que el archivo original)
        # Límite de 5MB -> ~6.7MB en base64
        if len(value) > 7000000:  # ~7MB en base64
            raise serializers.ValidationError(
                "El archivo es demasiado grande. Máximo 5MB."
            )
        
        return value

class AprobacionArriendoSerializer(serializers.Serializer):
    """Serializer para aprobar o rechazar solicitudes"""
    ACCIONES = [
        ('APROBAR', 'Aprobar'),
        ('RECHAZAR', 'Rechazar')
    ]
    
    accion = serializers.ChoiceField(choices=ACCIONES)
    observaciones = serializers.CharField(required=False, allow_blank=True, max_length=500)
    monto_pago = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        min_value=0
    )
    
    def validate(self, data):
        """Validaciones cruzadas"""
        accion = data.get('accion')
        monto_pago = data.get('monto_pago')
        
        if accion == 'APROBAR' and not monto_pago:
            raise serializers.ValidationError({
                'monto_pago': 'El monto de pago es obligatorio al aprobar una solicitud.'
            })
        
        if accion == 'RECHAZAR' and not data.get('observaciones'):
            raise serializers.ValidationError({
                'observaciones': 'Las observaciones son obligatorias al rechazar una solicitud.'
            })
        
        return data
