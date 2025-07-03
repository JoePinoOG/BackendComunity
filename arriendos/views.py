from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import SolicitudArriendo
from .serializers import (
    SolicitudArriendoSerializer,
    ComprobantePagoSerializer,
    AprobacionArriendoSerializer
)

class SolicitudArriendoViewSet(viewsets.ModelViewSet):
    queryset = SolicitudArriendo.objects.all()
    serializer_class = SolicitudArriendoSerializer

    def perform_create(self, serializer):
        serializer.save(solicitante=self.request.user)

    def update(self, request, *args, **kwargs):
        """Sobrescribir update para manejar cambios de estado"""
        instance = self.get_object()
        
        # Si se está intentando cambiar el estado
        if 'estado' in request.data:
            nuevo_estado = request.data['estado']
            
            # Solo validar si realmente se está cambiando el estado
            if nuevo_estado != instance.estado:
                # Validar permisos para cambiar estado
                if nuevo_estado in ['APROBADO', 'CANCELADO']:
                    # Solo tesorero o presidente pueden aprobar/rechazar
                    if not hasattr(request.user, 'rol') or request.user.rol not in ['TESORERO', 'PRESIDENTE']:
                        return Response({
                            'error': 'No tienes permisos para cambiar el estado de solicitudes.'
                        }, status=status.HTTP_403_FORBIDDEN)
                    
                    # Verificar que la solicitud esté pendiente
                    if instance.estado != 'PENDIENTE':
                        return Response({
                            'error': 'Solo se pueden modificar solicitudes pendientes.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # Validar transiciones de estado válidas
                valid_transitions = {
                    'PENDIENTE': ['APROBADO', 'CANCELADO'],
                    'APROBADO': ['PAGADO', 'CANCELADO'],
                    'PAGADO': [],
                    'CANCELADO': []
                }
                
                if nuevo_estado not in valid_transitions.get(instance.estado, []):
                    return Response({
                        'error': f'No se puede cambiar de {instance.estado} a {nuevo_estado}.'
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        # Continuar con la actualización normal
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='aprobar')
    def aprobar_solicitud(self, request, pk=None):
        """Endpoint para aprobar o rechazar solicitudes de arriendo"""
        solicitud = self.get_object()
        
        # Verificar que la solicitud esté pendiente
        if solicitud.estado != 'PENDIENTE':
            return Response({
                'error': 'Solo se pueden aprobar solicitudes pendientes.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar permisos (solo tesorero o presidente pueden aprobar)
        if not hasattr(request.user, 'rol') or request.user.rol not in ['TESORERO', 'PRESIDENTE']:
            return Response({
                'error': 'No tienes permisos para aprobar solicitudes.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AprobacionArriendoSerializer(data=request.data)
        if serializer.is_valid():
            accion = serializer.validated_data['accion']
            observaciones = serializer.validated_data.get('observaciones', '')
            monto_pago = serializer.validated_data.get('monto_pago')
            
            if accion == 'APROBAR':
                solicitud.estado = 'APROBADO'
                if monto_pago:
                    solicitud.monto_pago = monto_pago
                if observaciones:
                    solicitud.observaciones = observaciones
                mensaje = f"Solicitud de arriendo aprobada exitosamente."
            else:  # RECHAZAR
                solicitud.estado = 'CANCELADO'
                solicitud.observaciones = observaciones
                mensaje = f"Solicitud de arriendo rechazada."
            
            solicitud.save()
            
            return Response({
                'mensaje': mensaje,
                'solicitud': SolicitudArriendoSerializer(solicitud).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='subir-comprobante')
    def subir_comprobante(self, request, pk=None):
        """Endpoint para subir comprobante de pago"""
        solicitud = self.get_object()
        
        # Verificar que el usuario sea el solicitante
        if solicitud.solicitante != request.user:
            return Response({
                'error': 'No tienes permiso para subir comprobante a esta solicitud.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar que la solicitud esté en estado adecuado
        if solicitud.estado not in ['PENDIENTE', 'APROBADO', 'PAGADO']:
            return Response({
                'error': 'No se puede subir comprobante para solicitudes canceladas.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ComprobantePagoSerializer(solicitud, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensaje': 'Comprobante de pago subido exitosamente.',
                'comprobante_url': solicitud.comprobante_pago.url if solicitud.comprobante_pago else None
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DisponibilidadArriendoAPIView(APIView):
    def get(self, request):
        fecha = request.query_params.get('fecha')
        if not fecha:
            return Response({'error': 'Debe indicar una fecha'}, status=400)
        reservas = SolicitudArriendo.objects.filter(
            fecha_evento=fecha,
            estado__in=['PENDIENTE', 'APROBADO', 'PAGADO']
        )
        horarios_ocupados = [
            {'inicio': r.hora_inicio.strftime('%H:%M'), 'fin': r.hora_fin.strftime('%H:%M')}
            for r in reservas
        ]
        return Response({'ocupados': horarios_ocupados})