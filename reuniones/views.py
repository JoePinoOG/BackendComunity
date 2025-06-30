from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Reunion, Acta
from .serializers import ReunionSerializer, ActaSerializer, ValidarActaSerializer

class ReunionViewSet(viewsets.ModelViewSet):
    queryset = Reunion.objects.all().order_by('-fecha')
    serializer_class = ReunionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(convocante=self.request.user)

    @action(detail=True, methods=['post'])
    def notificar(self, request, pk=None):
        return Response({'status': 'Notificaciones enviadas'})

class ActaViewSet(viewsets.ModelViewSet):
    queryset = Acta.objects.all()
    serializer_class = ActaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

    @action(detail=True, methods=['post'])
    def validar(self, request, pk=None):
        acta = self.get_object()
        serializer = ValidarActaSerializer(data=request.data)
        
        if serializer.is_valid():
            return Response({'status': 'Acta actualizada'})
        
        return Response(serializer.errors, status=400)