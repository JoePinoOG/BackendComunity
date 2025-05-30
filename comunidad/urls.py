from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JuntaVecinosViewSet,
    SedeComunitariaViewSet,
    AnuncioViewSet,
    ContactoAutoridadViewSet,
)

# Crea el enrutador
router = DefaultRouter()
router.register(r'juntas', JuntaVecinosViewSet)
router.register(r'sedes', SedeComunitariaViewSet)
router.register(r'anuncios', AnuncioViewSet)
router.register(r'contactos', ContactoAutoridadViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
