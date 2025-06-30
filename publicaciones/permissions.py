from rest_framework.permissions import BasePermission

class PuedeCrearPublicaciones(BasePermission):
    """
    Permite crear publicaciones a usuarios autenticados
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

class PuedeEditarPublicacion(BasePermission):
    """
    Permite editar solo las publicaciones propias o roles administrativos
    """
    def has_object_permission(self, request, view, obj):
        # El autor puede editar su publicación
        if request.user == obj.autor:
            return True
        
        # Roles administrativos pueden editar cualquier publicación
        if request.user.rol in ['PRESIDENTE', 'SECRETARIO']:
            return True
        
        return False
