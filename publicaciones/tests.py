from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Publicacion

User = get_user_model()

class PublicacionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_publicacion_creation_with_image_base64(self):
        """Test crear publicación con imagen en base64"""
        imagen_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        publicacion = Publicacion.objects.create(
            titulo="Publicación de prueba",
            contenido="Contenido de prueba",
            tipo="ANUNCIO",
            imagen=imagen_base64,
            autor=self.user
        )
        
        self.assertEqual(publicacion.titulo, "Publicación de prueba")
        self.assertEqual(publicacion.imagen, imagen_base64)
        self.assertTrue(publicacion.esta_vigente())
    
    def test_publicacion_creation_without_image(self):
        """Test crear publicación sin imagen"""
        publicacion = Publicacion.objects.create(
            titulo="Publicación sin imagen",
            contenido="Contenido de prueba",
            tipo="NOTICIA",
            autor=self.user
        )
        
        self.assertEqual(publicacion.titulo, "Publicación sin imagen")
        self.assertIsNone(publicacion.imagen)
        self.assertTrue(publicacion.esta_vigente())
