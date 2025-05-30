from rest_framework.permissions import BasePermission

class EsSolicitante(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.solicitante == request.user

class EsDirectiva(BasePermission):
    def has_permission(self, request, view):
        return request.user.rol in ['PRESIDENTE', 'SECRETARIO']