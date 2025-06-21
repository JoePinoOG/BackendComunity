from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .models import CertificadoResidencia, SolicitudCertificado, TransaccionWebpay
from .serializers import (
    CertificadoResidenciaSerializer,
    SolicitudInicialSerializer,
    WebpayResponseSerializer,
    SolicitudCertificadoSerializer
)
from docxtpl import DocxTemplate
from datetime import datetime
import os
import tempfile
import requests
import json

class ConfigCertificadoAPIView(generics.RetrieveAPIView):
    """
    Obtiene la configuración actual del certificado
    """
    serializer_class = CertificadoResidenciaSerializer
    
    def get_object(self):
        return CertificadoResidencia.objects.first()

class SolicitudCertificadoCreateAPIView(generics.CreateAPIView):
    """
    Crea una nueva solicitud de certificado e inicia el pago Webpay
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SolicitudInicialSerializer

    def create(self, request, *args, **kwargs):
        # Validar datos con el serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        config = CertificadoResidencia.objects.first()
        if not config:
            return Response(
                {'error': 'Configuración no disponible'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Crear solicitud
        solicitud = SolicitudCertificado.objects.create(
            usuario=request.user,
            datos=serializer.validated_data,
            monto=config.precio,
            estado_pago='PENDIENTE',
            estado_documento='PENDIENTE'
        )
        
        # Iniciar pago Webpay
        try:
            webpay_config = settings.WEBPAY_CONFIG
            payload = {
                'buy_order': str(solicitud.id),
                'session_id': str(request.user.id),
                'amount': float(solicitud.monto),
                'return_url': webpay_config['CALLBACK_URL']
            }
            
            headers = {
                'Tbk-Api-Key-Id': webpay_config['COMMERCE_CODE'],
                'Tbk-Api-Key-Secret': webpay_config['API_KEY'],
                'Content-Type': 'application/json'
            }
            
            base_url = 'https://webpay3gint.transbank.cl' if webpay_config['ENVIRONMENT'] == 'TEST' else 'https://webpay3g.transbank.cl'
            url = f"{base_url}/rswebpaytransaction/api/webpay/v1.2/transactions"
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Guardar transacción
            TransaccionWebpay.objects.create(
                solicitud=solicitud,
                token=data['token'],
                estado='INICIADA',
                respuesta=data
            )
            
            # Preparar respuesta
            pago_serializer = WebpayResponseSerializer(data={
                'url_redirect': f"{base_url}/webpay/v1.2/transactions/{data['token']}",
                'token': data['token']
            })
            pago_serializer.is_valid(raise_exception=True)
            
            return Response({
                'solicitud': SolicitudCertificadoSerializer(solicitud).data,
                'pago': pago_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            solicitud.estado_pago = 'RECHAZADO'
            solicitud.save()
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_502_BAD_GATEWAY
            )

class WebpayCallbackAPIView(APIView):
    """
    Maneja el callback de Webpay después del pago
    """
    def get(self, request, *args, **kwargs):
        token = request.query_params.get('token_ws')
        if not token:
            return Response(
                {'error': 'Token no proporcionado'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verificar estado con Webpay
            transaccion = TransaccionWebpay.objects.get(token=token)
            webpay_config = settings.WEBPAY_CONFIG
            
            headers = {
                'Tbk-Api-Key-Id': webpay_config['COMMERCE_CODE'],
                'Tbk-Api-Key-Secret': webpay_config['API_KEY'],
                'Content-Type': 'application/json'
            }
            
            base_url = 'https://webpay3gint.transbank.cl' if webpay_config['ENVIRONMENT'] == 'TEST' else 'https://webpay3g.transbank.cl'
            url = f"{base_url}/rswebpaytransaction/api/webpay/v1.2/transactions/{token}"
            
            response = requests.put(url, headers=headers)
            data = response.json()
            
            # Actualizar transacción
            transaccion.respuesta = data
            transaccion.estado = 'APROBADA' if data['response_code'] == 0 else 'RECHAZADA'
            transaccion.save()
            
            # Actualizar solicitud
            solicitud = transaccion.solicitud
            solicitud.codigo_transaccion = data['buy_order']
            solicitud.respuesta_webpay = data
            solicitud.estado_pago = 'APROBADO' if data['response_code'] == 0 else 'RECHAZADO'
            solicitud.fecha_pago = datetime.now()
            
            if data['response_code'] == 0:
                self.generar_certificado(solicitud)
                solicitud.estado_documento = 'GENERADO'
                solicitud.fecha_generacion = datetime.now()
            
            solicitud.save()
            
            return Response(SolicitudCertificadoSerializer(solicitud).data)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def generar_certificado(self, solicitud):
        config = CertificadoResidencia.objects.first()
        if not config:
            raise Exception("Configuración no encontrada")
        
        try:
            doc = DocxTemplate(config.plantilla.path)
            
            contexto = {
                **solicitud.datos,
                'fecha_emision': datetime.now().strftime("%d de %B de %Y"),
                'firma_secretaria': "MAYRA CACERES CUEVAS",
                'firma_presidenta': "SONIA RUZ ALFARO"
            }
            
            doc.render(contexto)
            
            temp_dir = tempfile.gettempdir()
            filename = f"certificado_residencia_{solicitud.id}.docx"
            temp_path = os.path.join(temp_dir, filename)
            doc.save(temp_path)
            
            with open(temp_path, 'rb') as f:
                solicitud.documento.save(filename, f)
            
        except Exception as e:
            solicitud.estado_documento = 'ERROR'
            solicitud.save()
            raise e

class DescargarCertificadoAPIView(generics.RetrieveAPIView):
    """
    Permite descargar el certificado generado
    """
    permission_classes = [IsAuthenticated]
    queryset = SolicitudCertificado.objects.all()
    serializer_class = SolicitudCertificadoSerializer
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if not instance.documento:
            return Response(
                {'error': 'Documento no generado aún'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Marcar como entregado
        instance.estado_documento = 'ENTREGADO'
        instance.fecha_entrega = datetime.now()
        instance.save()
        
        # Devolver el archivo
        document = instance.documento.open('rb')
        response = FileResponse(document)
        response['Content-Disposition'] = f'attachment; filename="certificado_residencia_{instance.id}.docx"'
        return response
    
    def get_queryset(self):
        return super().get_queryset().filter(usuario=self.request.user)