from rest_framework.permissions import BasePermission

class EsTesorero(BasePermission):
    def has_permission(self, request, view):
        return request.user.rol == 'TESORERO'