from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Transaccion, CuentaPendiente
from .serializers import (
    TransaccionSerializer,
    CuentaPendienteSerializer,
    PagoSerializer
)
from .permissions import EsTesorero

class TransaccionViewSet(viewsets.ModelViewSet):
    queryset = Transaccion.objects.all().order_by('-fecha')
    serializer_class = TransaccionSerializer
    permission_classes = [EsTesorero]

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

    @action(detail=False, methods=['get'])
    def balance(self, request):
        ingresos = sum(t.monto for t in Transaccion.objects.filter(tipo='INGRESO'))
        egresos = sum(t.monto for t in Transaccion.objects.filter(tipo='EGRESO'))
        return Response({
            'ingresos': ingresos,
            'egresos': egresos,
            'balance': ingresos - egresos
        })

class CuentaPendienteViewSet(viewsets.ModelViewSet):
    queryset = CuentaPendiente.objects.all().order_by('fecha_vencimiento')
    serializer_class = CuentaPendienteSerializer
    permission_classes = [EsTesorero]

    @action(detail=True, methods=['post'])
    def pagar(self, request, pk=None):
        cuenta = self.get_object()
        serializer = PagoSerializer(data=request.data)
        
        if serializer.is_valid():
            cuenta.estado = 'PAGADA'
            cuenta.save()
            # Registrar transacción automática
            Transaccion.objects.create(
                tipo='EGRESO',
                monto=cuenta.monto,
                descripcion=f"Pago: {cuenta.nombre}",
                fecha=timezone.now().date(),
                creado_por=request.user
            )
            return Response({'status': 'Pago registrado'})
        
        return Response(serializer.errors, status=400)