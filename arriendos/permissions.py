from rest_framework import permissions

class EsTesoreroOPresidente(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a Tesoreros y Presidentes
    gestionar solicitudes de arriendo.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and
            hasattr(request.user, 'rol') and
            request.user.rol in ['TESORERO', 'PRESIDENTE']
        )

class EsPropietarioOTesoreroPresidente(permissions.BasePermission):
    """
    Permiso que permite al propietario de la solicitud o a admins (Tesorero/Presidente)
    acceder a la solicitud.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permitir al propietario de la solicitud
        if obj.solicitante == request.user:
            return True
            
        # Permitir a Tesorero y Presidente
        return (
            hasattr(request.user, 'rol') and
            request.user.rol in ['TESORERO', 'PRESIDENTE']
        )

class SoloPropietario(permissions.BasePermission):
    """
    Permiso que solo permite al propietario de la solicitud.
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.solicitante == request.user
