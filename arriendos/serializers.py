from rest_framework import serializers
from .models import SolicitudArriendo

class SolicitudArriendoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudArriendo
        fields = [
            'id', 'solicitante', 'fecha_evento', 'hora_inicio', 'hora_fin',
            'motivo', 'cantidad_asistentes', 'estado', 'monto_pago', 'fecha_solicitud', 'observaciones'
        ]
        read_only_fields = ['id', 'estado', 'monto_pago', 'fecha_solicitud', 'solicitante']

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
