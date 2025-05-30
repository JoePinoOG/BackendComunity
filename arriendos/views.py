from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import SolicitudArriendo
from .serializers import (
    SolicitudArriendoSerializer,
    AprobarSolicitudSerializer,
    SubirComprobanteSerializer
)
from .permissions import EsSolicitante, EsDirectiva

class SolicitudArriendoViewSet(viewsets.ModelViewSet):
    queryset = SolicitudArriendo.objects.all()
    serializer_class = SolicitudArriendoSerializer

    def get_permissions(self):
        if self.action in ['create', 'retrieve', 'update']:
            return [EsSolicitante()]
        elif self.action in ['aprobar', 'list']:
            return [EsDirectiva()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(solicitante=self.request.user)

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        solicitud = self.get_object()
        serializer = AprobarSolicitudSerializer(data=request.data)
        
        if serializer.is_valid():
            accion = serializer.validated_data['accion']
            if accion == 'APROBAR':
                solicitud.estado = 'APROBADO'
                solicitud.monto_pago = serializer.validated_data.get('monto')
            else:
                solicitud.estado = 'RECHAZADO'
            
            solicitud.observaciones = serializer.validated_data.get('observaciones', '')
            solicitud.save()
            
            return Response({'status': 'Solicitud actualizada'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def subir_comprobante(self, request, pk=None):
        solicitud = self.get_object()
        serializer = SubirComprobanteSerializer(data=request.data)
        
        if serializer.is_valid():
            solicitud.comprobante_pago = serializer.validated_data['comprobante']
            solicitud.estado = 'PAGADO'
            solicitud.save()
            return Response({'status': 'Comprobante subido'})
        
        return Response(serializer.errors, status=400)