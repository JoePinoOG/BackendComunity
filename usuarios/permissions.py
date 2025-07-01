from rest_framework.permissions import BasePermission

class EsSecretario(BasePermission):
    def has_permission(self, request, view):
        return request.user.rol == 'SECRETARIO'

class EsDirectiva(BasePermission):
    def has_permission(self, request, view):
        return request.user.rol in ['SECRETARIO', 'TESORERO', 'PRESIDENTE']

class EsPresidente(BasePermission):
    """Permiso para usuarios con rol de presidente"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'PRESIDENTE'

class PuedeValidarUsuarios(BasePermission):
    """
    Permiso para validar usuarios - solo presidentes pueden validar roles de directiva
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Solo presidentes pueden validar usuarios
        return request.user.rol == 'PRESIDENTE'
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Solo presidentes pueden validar
        if request.user.rol != 'PRESIDENTE':
            return False
            
        # No puede validarse a sí mismo
        if obj.id == request.user.id:
            return False
            
        return True

class PuedeVerUsuariosPendientes(BasePermission):
    """
    Permiso para ver usuarios pendientes de validación
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'PRESIDENTE'