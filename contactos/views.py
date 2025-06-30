# views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from .models import Contacto
from .serializers import ContactoSerializer

class ContactoViewSet(viewsets.ModelViewSet):
    queryset = Contacto.objects.all()
    serializer_class = ContactoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """
        Solo usuarios con ciertos roles pueden crear, actualizar o eliminar
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Verificar que el usuario tenga el rol apropiado
            permission_classes = [permissions.IsAuthenticated, IsAuthorizedRole]
        else:
            # Para listar y ver detalles, solo necesita estar autenticado
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Asociar el contacto con la junta de vecinos del usuario"""
        user_profile = getattr(self.request.user, 'userprofile', None)
        junta_vecinos = getattr(user_profile, 'junta_vecinos', None) if user_profile else None
        serializer.save(junta_vecinos=junta_vecinos)
    
    @action(detail=False, methods=['get'])
    def por_junta(self, request):
        """Obtener contactos filtrados por junta de vecinos del usuario"""
        user_profile = getattr(request.user, 'userprofile', None)
        if user_profile and user_profile.junta_vecinos:
            contactos = self.queryset.filter(junta_vecinos=user_profile.junta_vecinos)
            serializer = self.get_serializer(contactos, many=True)
            return Response(serializer.data)
        return Response([])

# Permiso personalizado para roles autorizados
class IsAuthorizedRole(permissions.BasePermission):
    """
    Permiso personalizado para usuarios con roles específicos
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Asumiendo que tienes un campo 'rol' en tu modelo de usuario
        user_profile = getattr(request.user, 'userprofile', None)
        if user_profile and hasattr(user_profile, 'rol'):
            allowed_roles = ['TESORERO', 'PRESIDENTE', 'SECRETARIO']
            return user_profile.rol.upper() in allowed_roles
        
        return False