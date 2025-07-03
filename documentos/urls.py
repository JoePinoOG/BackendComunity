# urls.py
from django.urls import path
from .views import (
    ConfigCertificadoAPIView,
    SolicitudCertificadoCreateAPIView,
    SolicitudCertificadoListAPIView,
    DescargarCertificadoAPIView
)

urlpatterns = [
    path('certificado/config/', ConfigCertificadoAPIView.as_view(), name='certificado-config'),
    path('certificado/solicitar/', SolicitudCertificadoCreateAPIView.as_view(), name='solicitar-certificado'),
    path('certificado/mis-solicitudes/', SolicitudCertificadoListAPIView.as_view(), name='mis-certificados'),
    path('certificado/<int:id>/descargar/', DescargarCertificadoAPIView.as_view(), name='descargar-certificado'),
]