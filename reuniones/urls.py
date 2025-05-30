from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReunionViewSet, ActaViewSet

router = DefaultRouter()
router.register(r'reuniones', ReunionViewSet)
router.register(r'actas', ActaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'reuniones/<int:pk>/notificar/',
        ReunionViewSet.as_view({'post': 'notificar'})
    ),
    path(
        'actas/<int:pk>/validar/',
        ActaViewSet.as_view({'post': 'validar'})
    ),
]