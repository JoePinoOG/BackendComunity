from rest_framework.permissions import BasePermission

class PuedeAgendarReuniones(BasePermission):
    def has_permission(self, request, view):
        return request.user.rol in ['PRESIDENTE', 'SECRETARIO']

class PuedeEditarActa(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.creado_por:
            return True
        return request.user.rol == 'SECRETARIO'

class PuedeValidarActa(BasePermission):
    def has_permission(self, request, view):
        return request.user.rol in ['PRESIDENTE', 'SECRETARIO']