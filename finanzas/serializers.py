from rest_framework import serializers
from .models import Transaccion, CuentaPendiente
from usuarios.models import Usuario

class TransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion
        fields = '__all__'
        read_only_fields = ('creado_por', 'creado_en')

class CuentaPendienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuentaPendiente
        fields = '__all__'

class PagoSerializer(serializers.Serializer):
    metodo = serializers.CharField(max_length=50)
    referencia = serializers.CharField(max_length=100)