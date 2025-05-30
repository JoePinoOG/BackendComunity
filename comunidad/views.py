from rest_framework import viewsets
from .models import JuntaVecinos, SedeComunitaria, Anuncio, ContactoAutoridad
from .serializers import (
    JuntaVecinosSerializer,
    SedeComunitariaSerializer,
    AnuncioSerializer,
    ContactoAutoridadSerializer,
)
from .permissions import IsDirectivaOrReadOnly 

# View para Junta de Vecinos
class JuntaVecinosViewSet(viewsets.ModelViewSet):
    queryset = JuntaVecinos.objects.all()
    serializer_class = JuntaVecinosSerializer

# View para Sede Comunitaria
class SedeComunitariaViewSet(viewsets.ModelViewSet):
    queryset = SedeComunitaria.objects.all()
    serializer_class = SedeComunitariaSerializer

# View para Anuncios
class AnuncioViewSet(viewsets.ModelViewSet):
    queryset = Anuncio.objects.all().order_by('-fecha_publicacion')
    serializer_class = AnuncioSerializer
    permission_classes = [IsDirectivaOrReadOnly]  # 👈 Aplica el permiso

# View para Contactos de Autoridades
class ContactoAutoridadViewSet(viewsets.ModelViewSet):
    queryset = ContactoAutoridad.objects.all()
    serializer_class = ContactoAutoridadSerializer
