from rest_framework import serializers
from .models import SolicitudArriendo

class SolicitudArriendoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudArriendo
        fields = [
            'id', 'solicitante', 'fecha_evento', 'hora_inicio', 'hora_fin',
            'motivo', 'cantidad_asistentes', 'estado', 'monto_pago', 'comprobante_pago',
            'fecha_solicitud', 'observaciones', 'token_webpay'
        ]
        read_only_fields = ['id', 'estado', 'monto_pago', 'fecha_solicitud', 'solicitante', 'token_webpay']

    def validate(self, data):
        fecha = data['fecha_evento']
        hora_inicio = data['hora_inicio']
        hora_fin = data['hora_fin']

        # Busca reservas que se solapen en la misma fecha y horario
        solapadas = SolicitudArriendo.objects.filter(
            fecha_evento=fecha,
            estado__in=['PENDIENTE', 'PAGADO']
        ).filter(
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio
        )
        if solapadas.exists():
            raise serializers.ValidationError(
                "Ya existe una reserva para ese horario. Por favor, elige otro horario o fecha."
            )
        return data


class ComprobantePagoSerializer(serializers.ModelSerializer):
    """Serializer específico para subir comprobante de pago"""
    class Meta:
        model = SolicitudArriendo
        fields = ['comprobante_pago']
        
    def validate_comprobante_pago(self, value):
        """Validar que el archivo sea una imagen"""
        if value:
            # Verificar que sea una imagen
            if not value.content_type.startswith('image/'):
                raise serializers.ValidationError("El archivo debe ser una imagen.")
            
            # Verificar tamaño máximo (5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("El archivo no puede ser mayor a 5MB.")
                
        return value
