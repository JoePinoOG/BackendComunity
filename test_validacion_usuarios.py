from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from usuarios.models import HistorialValidacion

User = get_user_model()

class ValidacionUsuariosTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Crear presidente para las pruebas
        self.presidente = User.objects.create_user(
            username='presidente_test',
            email='presidente@test.com',
            password='testpass123',
            first_name='Presidente',
            last_name='Test',
            rol='PRESIDENTE',
            estado='APROBADO',
            rut='11111111-1'
        )
        
        # Crear usuario pendiente de validación
        self.usuario_pendiente = User.objects.create_user(
            username='secretario_test',
            email='secretario@test.com',
            password='testpass123',
            first_name='Secretario',
            last_name='Test',
            rol='SECRETARIO',
            estado='PENDIENTE',
            rut='22222222-2'
        )
        
        # Crear vecino (se aprueba automáticamente)
        self.vecino = User.objects.create_user(
            username='vecino_test',
            email='vecino@test.com',
            password='testpass123',
            first_name='Vecino',
            last_name='Test',
            rol='VECINO',
            estado='APROBADO',
            rut='33333333-3'
        )

    def test_registro_vecino_requiere_aprobacion(self):
        """Test que los vecinos ahora también requieren aprobación"""
        data = {
            'username': 'nuevo_vecino',
            'email': 'nuevo_vecino@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Nuevo',
            'last_name': 'Vecino',
            'rol': 'VECINO',
            'rut': '44444444-4',
            'direccion': 'Calle Test 123',
            'telefono': '123456789'
        }
        
        response = self.client.post('/api/auth/usuarios/registro/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['require_approval'])  # Ahora requiere aprobación
        
        # Verificar que el usuario fue creado pero está pendiente
        usuario = User.objects.get(username='nuevo_vecino')
        self.assertEqual(usuario.estado, 'PENDIENTE')  # Cambió de APROBADO a PENDIENTE

    def test_registro_directiva_pendiente(self):
        """Test que los roles de directiva quedan pendientes"""
        data = {
            'username': 'nuevo_tesorero',
            'email': 'nuevo_tesorero@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Nuevo',
            'last_name': 'Tesorero',
            'rol': 'TESORERO',
            'rut': '55555555-5',
            'direccion': 'Calle Test 456',
            'telefono': '987654321'
        }
        
        response = self.client.post('/api/auth/usuarios/registro/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['require_approval'])
        
        # Verificar que el usuario fue creado pero está pendiente
        usuario = User.objects.get(username='nuevo_tesorero')
        self.assertEqual(usuario.estado, 'PENDIENTE')

    def test_presidente_puede_ver_usuarios_pendientes(self):
        """Test que el presidente puede ver usuarios pendientes incluyendo vecinos"""
        self.client.force_authenticate(user=self.presidente)
        
        response = self.client.get('/api/auth/usuarios/usuarios_pendientes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 1)  # Solo el secretario_test está pendiente
        self.assertEqual(response.data['usuarios_pendientes'][0]['username'], 'secretario_test')

    def test_presidente_puede_aprobar_usuario(self):
        """Test que el presidente puede aprobar usuarios"""
        self.client.force_authenticate(user=self.presidente)
        
        data = {
            'accion': 'APROBAR',
            'observacion': 'Usuario aprobado para el rol de secretario'
        }
        
        response = self.client.post(
            f'/api/auth/usuarios/{self.usuario_pendiente.id}/validar_usuario/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el usuario fue aprobado
        self.usuario_pendiente.refresh_from_db()
        self.assertEqual(self.usuario_pendiente.estado, 'APROBADO')
        
        # Verificar que se creó el historial
        historial = HistorialValidacion.objects.filter(
            usuario_validado=self.usuario_pendiente
        ).first()
        self.assertIsNotNone(historial)
        self.assertEqual(historial.accion, 'APROBADO')

    def test_presidente_puede_rechazar_usuario(self):
        """Test que el presidente puede rechazar usuarios"""
        self.client.force_authenticate(user=self.presidente)
        
        data = {
            'accion': 'RECHAZAR',
            'observacion': 'No cumple con los requisitos'
        }
        
        response = self.client.post(
            f'/api/auth/usuarios/{self.usuario_pendiente.id}/validar_usuario/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el usuario fue rechazado
        self.usuario_pendiente.refresh_from_db()
        self.assertEqual(self.usuario_pendiente.estado, 'RECHAZADO')

    def test_vecino_no_puede_validar_usuarios(self):
        """Test que un vecino no puede validar usuarios"""
        self.client.force_authenticate(user=self.vecino)
        
        response = self.client.get('/api/auth/usuarios/usuarios_pendientes/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_puede_validarse_a_si_mismo(self):
        """Test que un presidente no puede validarse a sí mismo"""
        # Crear otro presidente pendiente
        presidente_pendiente = User.objects.create_user(
            username='presidente_pendiente',
            email='presidente_pendiente@test.com',
            password='testpass123',
            rol='PRESIDENTE',
            estado='PENDIENTE',
            rut='66666666-6'
        )
        
        self.client.force_authenticate(user=presidente_pendiente)
        
        data = {'accion': 'APROBAR'}
        response = self.client.post(
            f'/api/auth/usuarios/{presidente_pendiente.id}/validar_usuario/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_estadisticas_validacion(self):
        """Test endpoint de estadísticas"""
        self.client.force_authenticate(user=self.presidente)
        
        response = self.client.get('/api/auth/usuarios/estadisticas_validacion/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        stats = response.data
        self.assertIn('pendientes', stats)
        self.assertIn('aprobados', stats)
        self.assertIn('por_rol', stats)
        self.assertEqual(stats['pendientes'], 1)  # solo secretario_test
        self.assertEqual(stats['aprobados'], 2)   # presidente y vecino (ya aprobados en setUp)
    
    def test_vecinos_tambien_aparecen_en_pendientes(self):
        """Test que los vecinos también aparecen en la lista de usuarios pendientes"""
        # Crear un vecino pendiente
        vecino_pendiente = User.objects.create_user(
            username='vecino_pendiente',
            email='vecino_pendiente@test.com',
            password='testpass123',
            first_name='Vecino',
            last_name='Pendiente',
            rol='VECINO',
            estado='PENDIENTE',
            rut='77777777-7'
        )
        
        self.client.force_authenticate(user=self.presidente)
        
        response = self.client.get('/api/auth/usuarios/usuarios_pendientes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Ahora deberían haber 2 usuarios pendientes: secretario_test y vecino_pendiente
        self.assertEqual(response.data['total'], 2)
        
        # Verificar que ambos roles están presentes
        usernames = [u['username'] for u in response.data['usuarios_pendientes']]
        self.assertIn('secretario_test', usernames)
        self.assertIn('vecino_pendiente', usernames)
