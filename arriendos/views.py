from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import SolicitudArriendo
from .serializers import (
    SolicitudArriendoSerializer
)
from django.conf import settings
from transbank.webpay.webpay_plus.transaction import Transaction

class SolicitudArriendoViewSet(viewsets.ModelViewSet):
    queryset = SolicitudArriendo.objects.all()
    serializer_class = SolicitudArriendoSerializer

    def perform_create(self, serializer):
        serializer.save(solicitante=self.request.user)

    @action(detail=True, methods=['post'])
    def iniciar_pago(self, request, pk=None):
        solicitud = self.get_object()
        if solicitud.estado != 'PENDIENTE':
            return Response({'error': 'La solicitud no está pendiente de pago.'}, status=status.HTTP_400_BAD_REQUEST)
        
        monto = 50000  # O el monto que corresponda según tu lógica
        buy_order = f"arriendo-{solicitud.id}"
        session_id = str(request.user.id)
        return_url = settings.WEBPAY_CONFIG['CALLBACK_URL']

        response = Transaction.create(
            buy_order=buy_order,
            session_id=session_id,
            amount=monto,
            return_url=return_url
        )
        token = response['token']
        url = response['url']

        solicitud.token_webpay = token
        solicitud.monto_pago = monto
        solicitud.save()

        return Response({'url': url, 'token': token})

class DisponibilidadArriendoAPIView(APIView):
    def get(self, request):
        fecha = request.query_params.get('fecha')
        if not fecha:
            return Response({'error': 'Debe indicar una fecha'}, status=400)
        reservas = SolicitudArriendo.objects.filter(
            fecha_evento=fecha,
            estado__in=['PENDIENTE', 'PAGADO']
        )
        horarios_ocupados = [
            {'inicio': r.hora_inicio.strftime('%H:%M'), 'fin': r.hora_fin.strftime('%H:%M')}
            for r in reservas
        ]
        return Response({'ocupados': horarios_ocupados})

class WebpayArriendoCallbackAPIView(APIView):
    permission_classes = []  # Permitir acceso sin autenticación

    def post(self, request):
        token_ws = request.data.get('token_ws') or request.query_params.get('token_ws')
        if not token_ws:
            return Response({'error': 'Token no proporcionado'}, status=400)
        
        solicitud = get_object_or_404(SolicitudArriendo, token_webpay=token_ws)
        
        if solicitud.estado == 'PAGADO':
            return Response({'error': 'Esta reserva ya fue pagada y está bloqueada.'}, status=400)
        
        solicitud.estado = 'PAGADO'
        solicitud.save()
        return Response({'status': 'Pago confirmado y reserva realizada'})