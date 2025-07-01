from rest_framework import viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

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
        """Crear publicación con el usuario autenticado como autor"""
        try:
            publicacion = serializer.save(autor=self.request.user)
            return publicacion
        except Exception as e:
            raise serializers.ValidationError(f"Error al crear la publicación: {str(e)}")
    
    def create(self, request, *args, **kwargs):
        """Override para manejar mejor los errores de creación"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            except Exception as e:
                return Response(
                    {"error": f"Error al crear la publicación: {str(e)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def incrementar_vistas(self, request, pk=None):
        """Incrementar el contador de vistas de una publicación"""
        publicacion = self.get_object()
        publicacion.incrementar_vistas()
        return Response({'vistas': publicacion.vistas})
    
    @action(detail=False, methods=['get'])
    def destacadas(self, request):
        """Obtener publicaciones destacadas"""
        publicaciones = self.queryset.filter(es_destacada=True, estado='ACTIVA')
        serializer = self.get_serializer(publicaciones, many=True)
        return Response(serializer.data)
