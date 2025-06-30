from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger(__name__)

from .models import Reunion, Acta
from .serializers import (
    ReunionSerializer,
    ActaSerializer,
    ValidarActaSerializer
)
from .permissions import (
    PuedeAgendarReuniones,
    PuedeEditarActa,
    PuedeValidarActa
)

class ReunionViewSet(viewsets.ModelViewSet):
    queryset = Reunion.objects.all().order_by('-fecha')
    serializer_class = ReunionSerializer
    permission_classes = [IsAuthenticated]  # Temporal: Solo autenticación

    def create(self, request, *args, **kwargs):
        logger.info(f"Intento de crear reunión por usuario: {request.user}")
        logger.info(f"Rol del usuario: {getattr(request.user, 'rol', 'Sin rol')}")
        logger.info(f"Datos recibidos: {request.data}")
        
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(convocante=self.request.user)

    @action(detail=True, methods=['post'])
    def notificar(self, request, pk=None):
        # Lógica para enviar notificaciones push/email
        return Response({'status': 'Notificaciones enviadas'})

class ActaViewSet(viewsets.ModelViewSet):
    queryset = Acta.objects.all()
    serializer_class = ActaSerializer
    permission_classes = [IsAuthenticated, PuedeEditarActa]

    @action(detail=True, methods=['post'])
    def validar(self, request, pk=None):
        acta = self.get_object()
        serializer = ValidarActaSerializer(data=request.data)
        
        if serializer.is_valid():
            # Lógica de validación/firma
            return Response({'status': 'Acta actualizada'})
        
        return Response(serializer.errors, status=400)