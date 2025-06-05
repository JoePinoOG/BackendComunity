from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .forms import PlantillaDocumentoForm
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from .models import PlantillaDocumento, SolicitudDocumento
from .serializers import PlantillaDocumentoSerializer, SolicitudDocumentoSerializer
from .document_generator import generar_pdf_desde_plantilla
from rest_framework.parsers import MultiPartParser, FormParser

class PlantillaDocumentoViewSet(viewsets.ModelViewSet):
    queryset = PlantillaDocumento.objects.filter(activo=True)
    serializer_class = PlantillaDocumentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_permissions(self):
        """
        Solo los administradores pueden crear, actualizar o eliminar plantillas.
        Cualquier usuario autenticado puede verlas.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

class SolicitudDocumentoViewSet(viewsets.ModelViewSet):
    serializer_class = SolicitudDocumentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Los administradores pueden ver todas las solicitudes.
        Los usuarios normales solo pueden ver sus propias solicitudes.
        """
        user = self.request.user
        if user.is_staff:
            return SolicitudDocumento.objects.all()
        return SolicitudDocumento.objects.filter(solicitante=user)
    
    @action(detail=True, methods=['post'])
    def generar(self, request, pk=None):
        """
        Genera el documento a partir de la plantilla y los datos proporcionados.
        """
        solicitud = self.get_object()
        
        # Verificar si ya se generó el documento
        if solicitud.estado == 'generado':
            return Response(
                {"detail": "El documento ya ha sido generado."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generar el documento
        try:
            generar_pdf_desde_plantilla(solicitud)
            return Response(
                {"detail": "Documento generado exitosamente."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": f"Error al generar el documento: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def descargar(self, request, pk=None):
        """
        Permite descargar el documento generado.
        """
        solicitud = self.get_object()
        
        # Verificar si el documento existe
        if not solicitud.documento_generado:
            return Response(
                {"detail": "El documento aún no ha sido generado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Devolver el archivo para descarga
        return FileResponse(
            solicitud.documento_generado.open('rb'),
            as_attachment=True,
            filename=solicitud.documento_generado.name.split('/')[-1]
        )

@user_passes_test(lambda u: u.is_staff)
def subir_plantilla(request):
    if request.method == 'POST':
        form = PlantillaDocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plantilla subida exitosamente.')
            return redirect('lista_plantillas')
    else:
        form = PlantillaDocumentoForm()
    
    return render(request, 'documentos/subir_plantilla.html', {'form': form})
