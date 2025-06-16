from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Usuario
from .serializers import UsuarioSerializer, AprobarUsuarioSerializer
from .permissions import EsSecretario, EsDirectiva

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action == 'aprobar':
            return [IsAuthenticated(), EsSecretario()]
        return [IsAuthenticated(), EsDirectiva()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        direccion = serializer.validated_data.get('direccion')
        juntas_vecinos = asignar_junta_vecinos(direccion)  # Implementa esta función
        serializer.save(juntas_vecinos=juntas_vecinos, estado='PENDIENTE')
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        usuario = self.get_object()
        serializer = AprobarUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario.estado = serializer.validated_data['estado']
            usuario.save()
            return Response({'status': 'Estado actualizado'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)