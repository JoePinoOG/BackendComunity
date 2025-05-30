from rest_framework import serializers
from .models import SolicitudArriendo

class SolicitudArriendoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudArriendo
        fields = '__all__'
        read_only_fields = (
            'solicitante',
            'estado',
            'fecha_solicitud'
        )

class AprobarSolicitudSerializer(serializers.Serializer):
    accion = serializers.ChoiceField(
        choices=[('APROBAR', 'Aprobar'), ('RECHAZAR', 'Rechazar')]
    )
    monto = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    observaciones = serializers.CharField(required=False)

class SubirComprobanteSerializer(serializers.Serializer):
    comprobante = serializers.FileField()