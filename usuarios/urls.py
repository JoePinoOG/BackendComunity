from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('usuarios/<int:pk>/aprobar/', UsuarioViewSet.as_view({'post': 'aprobar'})),
]