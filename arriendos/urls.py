from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SolicitudArriendoViewSet

router = DefaultRouter()
router.register(r'solicitudes', SolicitudArriendoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'solicitudes/<int:pk>/aprobar/',
        SolicitudArriendoViewSet.as_view({'post': 'aprobar'})
    ),
    path(
        'solicitudes/<int:pk>/subir-comprobante/',
        SolicitudArriendoViewSet.as_view({'post': 'subir_comprobante'})
    ),
]