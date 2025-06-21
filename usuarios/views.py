from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Usuario
from .serializers import UsuarioSerializer
from rest_framework.views import APIView
from django.http import HttpResponse
from django.contrib.auth import get_user_model

def asignar_junta_vecinos(direccion):
    return None

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action == 'aprobar':
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)  # O usa logging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        direccion = serializer.validated_data.get('direccion')
        juntas_vecinos = asignar_junta_vecinos(direccion)  # Asegúrate de que esta función existe y funciona
        serializer.save(juntas_vecinos=juntas_vecinos)
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

class UsuarioMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

def crear_superusuario(request):
    User = get_user_model()
    if not User.objects.filter(username='superuser').exists():
        User.objects.create_superuser(
            username='superuser',
            email='ma.donosor@duocuc.cl',
            password='superuser1234',
            rut='11111111-1',
            direccion='Dirección admin',
            telefono='123456789',
            estado='APROBADO',
            rol='PRESIDENTE'
        )
        return HttpResponse("Superusuario creado")
    return HttpResponse("Ya existe un usuario con ese nombre")



