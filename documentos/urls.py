# urls.py
from django.urls import path
from .views import (
    ConfigCertificadoAPIView,
    SolicitudCertificadoCreateAPIView,
    WebpayCallbackAPIView,
    DescargarCertificadoAPIView
)

urlpatterns = [
    path('api/certificado/config/', ConfigCertificadoAPIView.as_view(), name='certificado-config'),
    path('api/certificado/solicitar/', SolicitudCertificadoCreateAPIView.as_view(), name='solicitar-certificado'),
    path('api/certificado/webpay-callback/', WebpayCallbackAPIView.as_view(), name='webpay-callback'),
    path('api/certificado/<int:id>/descargar/', DescargarCertificadoAPIView.as_view(), name='descargar-certificado'),
]