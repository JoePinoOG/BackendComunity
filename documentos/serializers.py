from rest_framework import serializers
from .models import PlantillaDocumento, SolicitudDocumento

class PlantillaDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantillaDocumento
        fields = ['id', 'nombre', 'descripcion', 'archivo', 'tipo', 'campos_requeridos', 'activo']

class SolicitudDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudDocumento
        fields = ['id', 'plantilla', 'datos_documento', 'estado', 'fecha_solicitud', 'fecha_generacion']
        read_only_fields = ['estado', 'fecha_generacion', 'documento_generado']
    
    def create(self, validated_data):
        # Asignar el usuario actual como solicitante
        validated_data['solicitante'] = self.context['request'].user
        return super().create(validated_data)
