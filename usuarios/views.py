from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.http import HttpResponse
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Usuario, HistorialValidacion
from .serializers import (
    UsuarioSerializer, 
    UsuarioValidacionSerializer,
    ValidarUsuarioSerializer,
    UsuarioRegistroSerializer
)
from .permissions import (
    EsPresidente, 
    PuedeValidarUsuarios, 
    PuedeVerUsuariosPendientes
)

def asignar_junta_vecinos(direccion):
    return None

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        if self.action == 'create' or self.action == 'registro':
            return [AllowAny()]
        elif self.action in ['validar_usuario', 'usuarios_pendientes', 'estadisticas_validacion']:
            return [EsPresidente()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'registro':
            return UsuarioRegistroSerializer
        elif self.action == 'usuarios_pendientes':
            return UsuarioValidacionSerializer
        elif self.action == 'validar_usuario':
            return ValidarUsuarioSerializer
        return UsuarioSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        direccion = serializer.validated_data.get('direccion')
        juntas_vecinos = asignar_junta_vecinos(direccion)
        usuario = serializer.save(juntas_vecinos=juntas_vecinos)
        
        # Mensaje diferente según el rol
        if usuario.rol in ['SECRETARIO', 'TESORERO', 'PRESIDENTE']:
            mensaje = "Usuario registrado. Pendiente de aprobación por el presidente."
        else:
            mensaje = "Usuario registrado y aprobado automáticamente."
        
        return Response({
            'usuario': UsuarioSerializer(usuario).data,
            'mensaje': mensaje
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='registro')
    def registro(self, request):
        """Endpoint específico para registro de usuarios"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            
            if usuario.rol in ['SECRETARIO', 'TESORERO', 'PRESIDENTE']:
                mensaje = "Registro exitoso. Tu solicitud está pendiente de aprobación por el presidente."
                require_approval = True
            else:
                mensaje = "Registro exitoso. Tu cuenta ha sido aprobada automáticamente."
                require_approval = False
            
            return Response({
                'mensaje': mensaje,
                'require_approval': require_approval,
                'usuario_id': usuario.id,
                'estado': usuario.estado
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[EsPresidente])
    def usuarios_pendientes(self, request):
        """Obtener usuarios pendientes de validación"""
        usuarios_pendientes = Usuario.objects.filter(
            estado='PENDIENTE',
            rol__in=['SECRETARIO', 'TESORERO', 'PRESIDENTE']
        ).order_by('date_joined')
        
        serializer = UsuarioValidacionSerializer(usuarios_pendientes, many=True)
        return Response({
            'usuarios_pendientes': serializer.data,
            'total': usuarios_pendientes.count()
        })

    @action(detail=True, methods=['post'], permission_classes=[PuedeValidarUsuarios])
    def validar_usuario(self, request, pk=None):
        """Validar (aprobar o rechazar) un usuario"""
        usuario = self.get_object()
        
        # Verificar que el usuario esté pendiente
        if usuario.estado != 'PENDIENTE':
            return Response({
                'error': 'Este usuario no está pendiente de validación'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que no se esté validando a sí mismo
        if usuario.id == request.user.id:
            return Response({
                'error': 'No puedes validar tu propio registro'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ValidarUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            accion = serializer.validated_data['accion']
            observacion = serializer.validated_data.get('observacion', '')
            
            if accion == 'APROBAR':
                usuario.estado = 'APROBADO'
                mensaje = f"Usuario {usuario.get_full_name()} aprobado exitosamente"
                accion_historial = 'APROBADO'
            else:  # RECHAZAR
                usuario.estado = 'RECHAZADO'
                mensaje = f"Usuario {usuario.get_full_name()} rechazado"
                accion_historial = 'RECHAZADO'
            
            usuario.save()
            
            # Registrar en el historial
            HistorialValidacion.objects.create(
                usuario_validado=usuario,
                validado_por=request.user,
                accion=accion_historial,
                observacion=observacion
            )
            
            # Aquí podrías agregar logging o notificaciones
            return Response({
                'mensaje': mensaje,
                'usuario': UsuarioValidacionSerializer(usuario).data,
                'observacion': observacion
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[EsPresidente])
    def estadisticas_validacion(self, request):
        """Estadísticas de usuarios por estado"""
        stats = {
            'pendientes': Usuario.objects.filter(estado='PENDIENTE').count(),
            'aprobados': Usuario.objects.filter(estado='APROBADO').count(),
            'rechazados': Usuario.objects.filter(estado='RECHAZADO').count(),
            'total': Usuario.objects.count(),
            'por_rol': {}
        }
        
        # Estadísticas por rol
        for rol_code, rol_name in Usuario.ROLES:
            stats['por_rol'][rol_code] = {
                'nombre': rol_name,
                'total': Usuario.objects.filter(rol=rol_code).count(),
                'pendientes': Usuario.objects.filter(rol=rol_code, estado='PENDIENTE').count(),
                'aprobados': Usuario.objects.filter(rol=rol_code, estado='APROBADO').count(),
                'rechazados': Usuario.objects.filter(rol=rol_code, estado='RECHAZADO').count(),
            }
        
        return Response(stats)

    @action(detail=False, methods=['get'], permission_classes=[EsPresidente])
    def historial_validaciones(self, request):
        """Obtener historial completo de validaciones"""
        historial = HistorialValidacion.objects.select_related(
            'usuario_validado', 'validado_por'
        ).all()[:50]  # Últimas 50 validaciones
        
        data = []
        for record in historial:
            data.append({
                'id': record.id,
                'usuario_validado': {
                    'id': record.usuario_validado.id,
                    'username': record.usuario_validado.username,
                    'nombre_completo': record.usuario_validado.get_full_name(),
                    'rol': record.usuario_validado.get_rol_display()
                },
                'validado_por': {
                    'id': record.validado_por.id,
                    'username': record.validado_por.username,
                    'nombre_completo': record.validado_por.get_full_name()
                },
                'accion': record.accion,
                'observacion': record.observacion,
                'fecha_validacion': record.fecha_validacion
            })
        
        return Response({
            'historial': data,
            'total_registros': HistorialValidacion.objects.count()
        })

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """Método legacy para mantener compatibilidad"""
        return self.validar_usuario(request, pk)

class UsuarioMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personalizado que valida el estado del usuario antes del login"""
    
    def validate(self, attrs):
        # Primero validamos las credenciales usando el método padre
        data = super().validate(attrs)
        
        # Obtenemos el usuario autenticado
        user = self.user
        
        # Verificamos que el usuario esté aprobado
        if user.estado != 'APROBADO':
            if user.estado == 'PENDIENTE':
                error_msg = "Tu cuenta está pendiente de aprobación por el presidente. No puedes acceder hasta que sea aprobada."
            elif user.estado == 'RECHAZADO':
                error_msg = "Tu cuenta ha sido rechazada. Contacta al administrador para más información."
            else:
                error_msg = "Tu cuenta no está habilitada para acceder al sistema."
            
            from rest_framework import serializers
            raise serializers.ValidationError(error_msg)
        
        # Si llegamos aquí, el usuario está aprobado
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista personalizada de login que valida el estado del usuario"""
    serializer_class = CustomTokenObtainPairSerializer





