from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, UsuarioMeView, CustomTokenObtainPairView

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')

urlpatterns = [
    path('', include(router.urls)),
    path('me/', UsuarioMeView.as_view()),
    path('login/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
]