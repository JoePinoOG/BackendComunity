from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlantillaDocumentoViewSet, SolicitudDocumentoViewSet

router = DefaultRouter()
router.register(r'plantillas', PlantillaDocumentoViewSet)
router.register(r'solicitudes', SolicitudDocumentoViewSet, basename='solicitud')

urlpatterns = [
    path('', include(router.urls)),
]