from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
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
    permission_classes = [PuedeAgendarReuniones]

    def perform_create(self, serializer):
        serializer.save(convocante=self.request.user)

    @action(detail=True, methods=['post'])
    def notificar(self, request, pk=None):
        # Lógica para enviar notificaciones push/email
        return Response({'status': 'Notificaciones enviadas'})

class ActaViewSet(viewsets.ModelViewSet):
    queryset = Acta.objects.all()
    serializer_class = ActaSerializer
    permission_classes = [PuedeEditarActa]

    @action(detail=True, methods=['post'])
    def validar(self, request, pk=None):
        acta = self.get_object()
        serializer = ValidarActaSerializer(data=request.data)
        
        if serializer.is_valid():
            # Lógica de validación/firma
            return Response({'status': 'Acta actualizada'})
        
        return Response(serializer.errors, status=400)