# urls.py (en tu app)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactoViewSet

router = DefaultRouter()
router.register(r'', ContactoViewSet, basename='contacto')

urlpatterns = [
    path('', include(router.urls)),
]