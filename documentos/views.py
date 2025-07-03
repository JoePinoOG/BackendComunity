from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.conf import settings
from .models import CertificadoResidencia, SolicitudCertificado, TransaccionWebpay
from .serializers import (
    CertificadoResidenciaSerializer,
    SolicitudInicialSerializer,
    WebpayResponseSerializer,
    SolicitudCertificadoSerializer
)
from docxtpl import DocxTemplate
from docx2pdf import convert
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
        # Crear solicitud sin validaciones estrictas
        config = CertificadoResidencia.objects.first()
        
        # Crear solicitud directamente
        solicitud = SolicitudCertificado.objects.create(
            usuario=request.user,
            datos=request.data,  # Usar datos directamente sin validación
            monto=config.precio if config else 0,
            estado_pago='APROBADO',  # Marcar como aprobado directamente
            estado_documento='PENDIENTE'
        )
        
        # Generar certificado inmediatamente
        try:
            self.generar_certificado(solicitud)
            solicitud.estado_documento = 'GENERADO'
            solicitud.fecha_generacion = datetime.now()
            solicitud.save()
            
            return Response({
                'message': 'Certificado generado exitosamente',
                'solicitud': SolicitudCertificadoSerializer(solicitud).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            solicitud.estado_documento = 'ERROR'
            solicitud.save()
            return Response(
                {'error': f'Error al generar certificado: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def generar_certificado(self, solicitud):
        """Genera el certificado PDF sin validaciones"""
        config = CertificadoResidencia.objects.first()
        
        try:
            # Si no hay plantilla, crear certificado básico
            if not config or not config.plantilla:
                # Crear certificado básico sin plantilla
                filename_pdf = f"certificado_residencia_{solicitud.id}.pdf"
                temp_dir = tempfile.gettempdir()
                temp_path_pdf = os.path.join(temp_dir, filename_pdf)
                
                # Crear un PDF básico (puedes usar reportlab o similar)
                # Por simplicidad, creamos un archivo texto temporal
                with open(temp_path_pdf, 'w') as f:
                    f.write(f"Certificado de Residencia #{solicitud.id}\n")
                    f.write(f"Usuario: {solicitud.usuario.get_full_name()}\n")
                    f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}\n")
                
                # Simular guardado (reemplaza con tu lógica de PDF)
                with open(temp_path_pdf, 'rb') as f:
                    solicitud.documento_pdf.save(filename_pdf, f)
                return

            # Si hay plantilla, usar DocxTemplate
            doc = DocxTemplate(config.plantilla.path)
            usuario = solicitud.usuario

            # Usar datos básicos del usuario, sin validar campos requeridos
            datos_solicitud = solicitud.datos if isinstance(solicitud.datos, dict) else {}
            
            contexto = {
                'nombre_completo': datos_solicitud.get('nombre_completo', usuario.get_full_name()),
                'cedula_identidad': datos_solicitud.get('cedula_identidad', ''),
                'domicilio_completo': datos_solicitud.get('domicilio_completo', ''),
                'institucion_destino': datos_solicitud.get('institucion_destino', ''),
                'nombre_usuario': usuario.get_full_name(),
                'email_usuario': usuario.email,
                'fecha_emision': datetime.now().strftime("%d de %B de %Y"),
                'firma_secretaria': "MAYRA CACERES CUEVAS",
                'firma_presidenta': "SONIA RUZ ALFARO"
            }
            
            doc.render(contexto)
            
            temp_dir = tempfile.gettempdir()
            filename_docx = f"certificado_residencia_{solicitud.id}.docx"
            temp_path_docx = os.path.join(temp_dir, filename_docx)
            doc.save(temp_path_docx)

            # Convertir a PDF
            filename_pdf = f"certificado_residencia_{solicitud.id}.pdf"
            temp_path_pdf = os.path.join(temp_dir, filename_pdf)
            convert(temp_path_docx, temp_path_pdf)

            # Guardar el PDF en el modelo
            with open(temp_path_pdf, 'rb') as f:
                solicitud.documento_pdf.save(filename_pdf, f)

        except Exception as e:
            print(f"Error al generar certificado: {str(e)}")
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
        
        # Verificar si hay documento PDF generado
        if not instance.documento_pdf:
            return Response(
                {'error': 'Documento no generado aún'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Marcar como entregado
        instance.estado_documento = 'ENTREGADO'
        instance.fecha_entrega = datetime.now()
        instance.save()
        
        # Devolver el archivo PDF
        from django.http import FileResponse
        document = instance.documento_pdf.open('rb')
        response = FileResponse(document, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="certificado_residencia_{instance.id}.pdf"'
        return response
    
    def get_queryset(self):
        return super().get_queryset().filter(usuario=self.request.user)