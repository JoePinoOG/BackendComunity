from rest_framework.permissions import BasePermission

class EsSecretario(BasePermission):
    def has_permission(self, request, view):
        return request.user.rol == 'SECRETARIO'

class EsDirectiva(BasePermission):
    def has_permission(self, request, view):
        return request.user.rol in ['SECRETARIO', 'TESORERO', 'PRESIDENTE']