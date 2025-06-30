from rest_framework.permissions import BasePermission

class PuedeAgendarReuniones(BasePermission):
    def has_permission(self, request, view):
        # Verificar que el usuario esté autenticado
        if not request.user.is_authenticated:
            return False
        
        # Verificar que el usuario tenga el rol adecuado
        return hasattr(request.user, 'rol') and request.user.rol in ['PRESIDENTE', 'SECRETARIO']

class PuedeEditarActa(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Verificar que el usuario esté autenticado
        if not request.user.is_authenticated:
            return False
            
        if request.user == obj.creado_por:
            return True
        return hasattr(request.user, 'rol') and request.user.rol == 'SECRETARIO'

class PuedeValidarActa(BasePermission):
    def has_permission(self, request, view):
        # Verificar que el usuario esté autenticado
        if not request.user.is_authenticated:
            return False
            
        return hasattr(request.user, 'rol') and request.user.rol in ['PRESIDENTE', 'SECRETARIO']