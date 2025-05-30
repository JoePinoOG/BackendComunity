from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransaccionViewSet, CuentaPendienteViewSet

router = DefaultRouter()
router.register(r'transacciones', TransaccionViewSet)
router.register(r'cuentas-pendientes', CuentaPendienteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'transacciones/balance/',
        TransaccionViewSet.as_view({'get': 'balance'})
    ),
    path(
        'cuentas-pendientes/<int:pk>/pagar/',
        CuentaPendienteViewSet.as_view({'post': 'pagar'})
    ),
]