from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SolicitudArriendoViewSet, DisponibilidadArriendoAPIView, EstadisticasArriendoAPIView

router = DefaultRouter()
router.register(r'solicitudes', SolicitudArriendoViewSet, basename='solicitudarriendo')

urlpatterns = [
    path('disponibilidad/', DisponibilidadArriendoAPIView.as_view(), name='disponibilidad-arriendo'),
    path('estadisticas/', EstadisticasArriendoAPIView.as_view(), name='estadisticas-arriendo'),
    path('', include(router.urls)),
]