from rest_framework import viewsets
from .models import Reunion
from .serializers import ReunionSerializer

class ReunionViewSet(viewsets.ModelViewSet):
    queryset = Reunion.objects.all().order_by('-fecha')
    serializer_class = ReunionSerializer