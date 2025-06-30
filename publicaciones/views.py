from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Publicacion
from .serializers import (
    PublicacionListSerializer,
    PublicacionDetailSerializer,
    PublicacionCreateUpdateSerializer
)
from .permissions import PuedeCrearPublicaciones, PuedeEditarPublicacion

class PublicacionViewSet(viewsets.ModelViewSet):
    queryset = Publicacion.objects.filter(estado='ACTIVA').select_related('autor')
    permission_classes = [IsAuthenticated, PuedeCrearPublicaciones]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'autor']
    search_fields = ['titulo', 'contenido']
    ordering_fields = ['fecha_creacion']
    ordering = ['-fecha_creacion']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PublicacionListSerializer
        elif self.action == 'retrieve':
            return PublicacionDetailSerializer
        else:  # create, update, partial_update
            return PublicacionCreateUpdateSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, PuedeEditarPublicacion]
        else:
            permission_classes = [IsAuthenticated, PuedeCrearPublicaciones]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)
