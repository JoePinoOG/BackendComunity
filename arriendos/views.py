from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import SolicitudArriendo
from .serializers import (
    SolicitudArriendoSerializer,
    SolicitudArriendoCreateSerializer,
    ComprobantePagoSerializer,
    AprobacionArriendoSerializer
)

class SolicitudArriendoViewSet(viewsets.ModelViewSet):
    queryset = SolicitudArriendo.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return SolicitudArriendoCreateSerializer
        return SolicitudArriendoSerializer

    def perform_create(self, serializer):
        serializer.save(solicitante=self.request.user)

    def get_queryset(self):
        # Si es admin, ver todas; si no, solo las propias
        if hasattr(self.request.user, 'rol') and self.request.user.rol in ['TESORERO', 'PRESIDENTE']:
            return SolicitudArriendo.objects.all()
        return SolicitudArriendo.objects.filter(solicitante=self.request.user)

    @action(detail=True, methods=['post'], url_path='aprobar')
    def aprobar_solicitud(self, request, pk=None):
        """Endpoint para aprobar o rechazar solicitudes de arriendo"""
        solicitud = self.get_object()
        
        # Verificar permisos (solo tesorero o presidente pueden aprobar)
        if not hasattr(request.user, 'rol') or request.user.rol not in ['TESORERO', 'PRESIDENTE']:
            return Response({
                'error': 'No tienes permisos para aprobar solicitudes.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar que la solicitud esté pendiente
        if solicitud.estado != 'PENDIENTE':
            return Response({
                'error': 'Solo se pueden modificar solicitudes pendientes.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
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
                mensaje = "Solicitud de arriendo aprobada exitosamente."
            else:  # RECHAZAR
                solicitud.estado = 'CANCELADO'
                solicitud.observaciones = observaciones
                mensaje = "Solicitud de arriendo rechazada."
            
            solicitud.save()
            
            return Response({
                'mensaje': mensaje,
                'solicitud': SolicitudArriendoSerializer(solicitud).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='subir-comprobante')
    def subir_comprobante(self, request, pk=None):
        """Endpoint para subir comprobante de pago en base64"""
        solicitud = self.get_object()
        
        # Verificar que el usuario sea el solicitante
        if solicitud.solicitante != request.user:
            return Response({
                'error': 'No tienes permiso para subir comprobante a esta solicitud.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar que la solicitud esté en estado adecuado
        if solicitud.estado not in ['PENDIENTE', 'APROBADO']:
            return Response({
                'error': 'Solo se puede subir comprobante para solicitudes pendientes o aprobadas.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ComprobantePagoSerializer(solicitud, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensaje': 'Comprobante de pago subido exitosamente.',
                'tiene_comprobante': bool(solicitud.comprobante_pago_base64)
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='marcar-pagado')
    def marcar_pagado(self, request, pk=None):
        """Endpoint para marcar como pagado (solo admins)"""
        solicitud = self.get_object()
        
        # Verificar permisos
        if not hasattr(request.user, 'rol') or request.user.rol not in ['TESORERO', 'PRESIDENTE']:
            return Response({
                'error': 'No tienes permisos para marcar como pagado.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if solicitud.estado != 'APROBADO':
            return Response({
                'error': 'Solo se pueden marcar como pagadas las solicitudes aprobadas.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        solicitud.estado = 'PAGADO'
        solicitud.save()
        
        return Response({
            'mensaje': 'Solicitud marcada como pagada.',
            'solicitud': SolicitudArriendoSerializer(solicitud).data
        })

class DisponibilidadArriendoAPIView(APIView):
    """Vista simple para verificar disponibilidad por fecha"""
    
    def get(self, request):
        fecha = request.query_params.get('fecha')
        if not fecha:
            return Response({'error': 'Debe indicar una fecha'}, status=400)
            
        reservas = SolicitudArriendo.objects.filter(
            fecha_evento=fecha,
            estado__in=['APROBADO', 'PAGADO']  # Solo las confirmadas
        )
        
        horarios_ocupados = [
            {
                'inicio': r.hora_inicio.strftime('%H:%M'), 
                'fin': r.hora_fin.strftime('%H:%M'),
                'motivo': r.motivo
            }
            for r in reservas
        ]
        
        return Response({'ocupados': horarios_ocupados})