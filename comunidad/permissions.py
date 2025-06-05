from rest_framework import permissions

class IsDirectivaOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que solo permite a los usuarios de la directiva
    modificar objetos. Los demás solo pueden verlos (lectura).
    """

    def has_permission(self, request, view):
        # Permitir solo lectura siempre
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permitir escritura solo a usuarios con rol de directiva
        return request.user.groups.filter(name__in=["Presidente", "Secretario", "Tesorero"]).exists()

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite a cualquier usuario autenticado crear/editar objetos.
    Los usuarios no autenticados solo pueden ver (lectura).
    """
    
    def has_permission(self, request, view):
        # Permitir solo lectura para cualquier usuario
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Permitir escritura solo a usuarios autenticados
        return request.user and request.user.is_authenticated
