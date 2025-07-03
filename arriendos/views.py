from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import models
from datetime import datetime, time
from .models import SolicitudArriendo
from .serializers import (
    SolicitudArriendoSerializer,
    SolicitudArriendoCreateSerializer,
    ComprobantePagoSerializer,
    AprobacionArriendoSerializer
)
from .permissions import (
    EsTesoreroOPresidente,
    EsPropietarioOTesoreroPresidente,
    SoloPropietario
)

class SolicitudArriendoViewSet(viewsets.ModelViewSet):
    queryset = SolicitudArriendo.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return SolicitudArriendoCreateSerializer
        return SolicitudArriendoSerializer

    def get_permissions(self):
        """
        Permisos específicos según la acción
        """
        if self.action in ['aprobar_solicitud', 'marcar_pagado']:
            permission_classes = [IsAuthenticated, EsTesoreroOPresidente]
        elif self.action == 'subir_comprobante':
            permission_classes = [IsAuthenticated, EsPropietarioOTesoreroPresidente]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Validaciones adicionales al crear una solicitud"""
        fecha_evento = serializer.validated_data['fecha_evento']
        hora_inicio = serializer.validated_data['hora_inicio']
        hora_fin = serializer.validated_data['hora_fin']
        
        # Validar que la fecha no sea en el pasado
        if fecha_evento < timezone.now().date():
            raise serializers.ValidationError("No se pueden crear solicitudes para fechas pasadas.")
        
        # Validar que la hora de inicio sea anterior a la hora de fin
        if hora_inicio >= hora_fin:
            raise serializers.ValidationError("La hora de inicio debe ser anterior a la hora de fin.")
        
        # Validar que no haya conflictos con otras reservas
        conflictos = SolicitudArriendo.objects.filter(
            fecha_evento=fecha_evento,
            estado__in=['APROBADO', 'PAGADO']
        ).exclude(
            # Excluir reservas que no se solapan
            models.Q(hora_fin__lte=hora_inicio) | models.Q(hora_inicio__gte=hora_fin)
        )
        
        if conflictos.exists():
            raise serializers.ValidationError(
                "Ya existe una reserva aprobada para ese horario. "
                "Por favor, selecciona otro horario."
            )
        
        serializer.save(solicitante=self.request.user)

    def get_queryset(self):
        """Filtrar solicitudes según el rol del usuario"""
        user = self.request.user
        
        # Si es admin (tesorero o presidente), ver todas
        if hasattr(user, 'rol') and user.rol in ['TESORERO', 'PRESIDENTE']:
            return SolicitudArriendo.objects.all().order_by('-fecha_solicitud')
        
        # Si es vecino regular, solo ver las propias
        return SolicitudArriendo.objects.filter(
            solicitante=user
        ).order_by('-fecha_solicitud')

    @action(detail=False, methods=['get'], url_path='mis-solicitudes')
    def mis_solicitudes(self, request):
        """Endpoint específico para obtener solicitudes del usuario actual"""
        solicitudes = SolicitudArriendo.objects.filter(
            solicitante=request.user
        ).order_by('-fecha_solicitud')
        
        serializer = self.get_serializer(solicitudes, many=True)
        return Response({
            'count': solicitudes.count(),
            'results': serializer.data
        })

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
    """Vista para verificar disponibilidad por fecha"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        fecha = request.query_params.get('fecha')
        if not fecha:
            return Response({
                'error': 'Debe indicar una fecha en formato YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Validar formato de fecha
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que no sea una fecha pasada
        if fecha_obj < timezone.now().date():
            return Response({
                'error': 'No se puede consultar disponibilidad para fechas pasadas'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Obtener reservas confirmadas para esa fecha
        reservas = SolicitudArriendo.objects.filter(
            fecha_evento=fecha_obj,
            estado__in=['APROBADO', 'PAGADO']
        ).order_by('hora_inicio')
        
        horarios_ocupados = []
        for reserva in reservas:
            horarios_ocupados.append({
                'inicio': reserva.hora_inicio.strftime('%H:%M'),
                'fin': reserva.hora_fin.strftime('%H:%M'),
                'motivo': reserva.motivo,
                'solicitante': reserva.solicitante.get_full_name(),
                'estado': reserva.estado
            })
        
        # Horarios disponibles (ejemplo: 8:00 - 22:00 en bloques de 1 hora)
        horarios_disponibles = []
        hora_actual = time(8, 0)
        hora_limite = time(22, 0)
        
        while hora_actual < hora_limite:
            hora_fin = time(hora_actual.hour + 1, hora_actual.minute)
            if hora_fin <= hora_limite:
                # Verificar si este bloque está ocupado
                bloque_ocupado = False
                for reserva in reservas:
                    if (hora_actual < reserva.hora_fin and hora_fin > reserva.hora_inicio):
                        bloque_ocupado = True
                        break
                
                if not bloque_ocupado:
                    horarios_disponibles.append({
                        'inicio': hora_actual.strftime('%H:%M'),
                        'fin': hora_fin.strftime('%H:%M')
                    })
            
            # Avanzar una hora
            hora_actual = time(hora_actual.hour + 1, hora_actual.minute)
        
        return Response({
            'fecha': fecha,
            'ocupados': horarios_ocupados,
            'disponibles': horarios_disponibles,
            'total_reservas': len(horarios_ocupados)
        })


class EstadisticasArriendoAPIView(APIView):
    """Vista para obtener estadísticas de arriendos - Solo para admins"""
    permission_classes = [IsAuthenticated, EsTesoreroOPresidente]
    
    def get(self, request):
        from django.db.models import Count, Sum, Q
        from django.utils import timezone
        from datetime import timedelta
        
        # Estadísticas generales
        total_solicitudes = SolicitudArriendo.objects.count()
        
        solicitudes_por_estado = SolicitudArriendo.objects.values('estado').annotate(
            cantidad=Count('id')
        ).order_by('estado')
        
        # Estadísticas del mes actual
        inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fin_mes = inicio_mes.replace(month=inicio_mes.month + 1) if inicio_mes.month < 12 else inicio_mes.replace(year=inicio_mes.year + 1, month=1)
        
        solicitudes_mes = SolicitudArriendo.objects.filter(
            fecha_solicitud__gte=inicio_mes,
            fecha_solicitud__lt=fin_mes
        ).count()
        
        ingresos_mes = SolicitudArriendo.objects.filter(
            fecha_solicitud__gte=inicio_mes,
            fecha_solicitud__lt=fin_mes,
            estado='PAGADO'
        ).aggregate(total=Sum('monto_pago'))['total'] or 0
        
        # Solicitudes pendientes de revisión
        pendientes_revision = SolicitudArriendo.objects.filter(
            estado='PENDIENTE'
        ).count()
        
        # Solicitudes con comprobante pendiente de validación
        con_comprobante_pendiente = SolicitudArriendo.objects.filter(
            estado='APROBADO',
            comprobante_pago_base64__isnull=False
        ).count()
        
        # Próximos eventos (solicitudes pagadas)
        proximos_eventos = SolicitudArriendo.objects.filter(
            estado='PAGADO',
            fecha_evento__gte=timezone.now().date()
        ).order_by('fecha_evento')[:5]
        
        eventos_data = []
        for evento in proximos_eventos:
            eventos_data.append({
                'id': evento.id,
                'fecha': evento.fecha_evento.strftime('%Y-%m-%d'),
                'hora_inicio': evento.hora_inicio.strftime('%H:%M'),
                'hora_fin': evento.hora_fin.strftime('%H:%M'),
                'motivo': evento.motivo,
                'solicitante': evento.solicitante.get_full_name(),
                'cantidad_asistentes': evento.cantidad_asistentes
            })
        
        return Response({
            'resumen': {
                'total_solicitudes': total_solicitudes,
                'solicitudes_mes': solicitudes_mes,
                'ingresos_mes': float(ingresos_mes),
                'pendientes_revision': pendientes_revision,
                'con_comprobante_pendiente': con_comprobante_pendiente
            },
            'por_estado': {item['estado']: item['cantidad'] for item in solicitudes_por_estado},
            'proximos_eventos': eventos_data
        })