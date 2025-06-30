from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Publicacion
from .serializers import (
    PublicacionListSerializer,
    PublicacionDetailSerializer,
    PublicacionCreateUpdateSerializer
)

class PublicacionViewSet(viewsets.ModelViewSet):
    queryset = Publicacion.objects.all().order_by('-fecha_creacion')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PublicacionListSerializer
        elif self.action == 'retrieve':
            return PublicacionDetailSerializer
        else:  # create, update, partial_update
            return PublicacionCreateUpdateSerializer
    
    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)
