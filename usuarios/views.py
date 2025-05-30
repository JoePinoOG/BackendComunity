from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Usuario
from .serializers import UsuarioSerializer, AprobarUsuarioSerializer
from .permissions import EsSecretario, EsDirectiva

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    @action(detail=True, methods=['post'], permission_classes=[EsSecretario])
    def aprobar(self, request, pk=None):
        usuario = self.get_object()
        serializer = AprobarUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario.estado = serializer.validated_data['estado']
            usuario.save()
            return Response({'status': 'Estado actualizado'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action == 'create':
            return []  # Cualquiera puede registrarse
        return [IsAuthenticated(), EsDirectiva()]

def create(self, request):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Lógica para asignar JJVV basada en dirección (ejemplo simplificado)
    direccion = serializer.validated_data.get('direccion')
    juntas_vecinos = asignar_junta_vecinos(direccion)  # Función a implementar
    
    serializer.save(juntas_vecinos=juntas_vecinos, estado='PENDIENTE')
    return Response(serializer.data, status=status.HTTP_201_CREATED)