from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SolicitudArriendoViewSet, DisponibilidadArriendoAPIView, WebpayArriendoCallbackAPIView

router = DefaultRouter()
router.register(r'solicitudes', SolicitudArriendoViewSet, basename='solicitudarriendo')

urlpatterns = [
    path('disponibilidad/', DisponibilidadArriendoAPIView.as_view(), name='disponibilidad-arriendo'),
    path('webpay-callback/', WebpayArriendoCallbackAPIView.as_view(), name='webpay-arriendo-callback'),
    path('', include(router.urls)),
    path(
        'solicitudes/<int:pk>/aprobar/',
        SolicitudArriendoViewSet.as_view({'post': 'aprobar'})
    ),
]