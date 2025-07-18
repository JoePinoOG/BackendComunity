from rest_framework import serializers
from .models import Reunion

class ReunionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reunion
        fields = ['id', 'titulo', 'fecha', 'lugar', 'motivo']