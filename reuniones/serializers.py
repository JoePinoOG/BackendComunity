from rest_framework import serializers
from .models import Reunion, Acta
from usuarios.models import Usuario

class ReunionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reunion
        fields = [
            'id', 'motivo', 'fecha', 'lugar', 'descripcion',
            'convocante', 'creada_en'
        ]
        read_only_fields = ('convocante', 'creada_en')

class ActaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acta
        fields = '__all__'
        read_only_fields = (
            'creado_por', 'estado',
            'firmado_presidente', 'firmado_secretario',
            'ultima_modificacion'
        )

class ValidarActaSerializer(serializers.Serializer):
    accion = serializers.ChoiceField(
        choices=[('FIRMAR', 'Firmar'), ('VALIDAR', 'Validar')]
    )