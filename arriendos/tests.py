from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import date, time, timedelta
from .models import SolicitudArriendo
from comunidad.models import JuntaVecinos

User = get_user_model()

class SolicitudArriendoModelTests(TestCase):
    def setUp(self):
        self.junta = JuntaVecinos.objects.create(
            nombre="Junta Test",
            direccion="Calle Test 123",
            sector="Sector Test"
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            rol='VECINO',
            juntas_vecinos=self.junta
        )
        
        self.solicitud = SolicitudArriendo.objects.create(
            solicitante=self.user,
            fecha_evento=date.today() + timedelta(days=7),
            hora_inicio=time(14, 0),
            hora_fin=time(18, 0),
            motivo="Cumpleaños",
            cantidad_asistentes=50
        )

    def test_crear_solicitud_valida(self):
        """Test crear una solicitud válida"""
        self.assertEqual(self.solicitud.estado, 'PENDIENTE')
        self.assertEqual(self.solicitud.solicitante, self.user)
        self.assertEqual(self.solicitud.duracion_horas, 4)

    def test_solicitud_str(self):
        """Test método __str__ del modelo"""
        expected = f"Solicitud #{self.solicitud.id} - {self.user.username} - {self.solicitud.fecha_evento}"
        self.assertEqual(str(self.solicitud), expected)

    def test_propiedades_solicitud(self):
        """Test propiedades del modelo"""
        self.assertFalse(self.solicitud.esta_pagado)
        self.assertFalse(self.solicitud.esta_aprobado)
        self.assertTrue(self.solicitud.puede_cancelar)
        self.assertFalse(self.solicitud.tiene_comprobante)

    def test_aprobar_solicitud(self):
        """Test aprobar solicitud"""
        self.solicitud.aprobar(monto_pago=50000, observaciones="Aprobado")
        self.assertEqual(self.solicitud.estado, 'APROBADO')
        self.assertEqual(self.solicitud.monto_pago, 50000)
        self.assertTrue(self.solicitud.esta_aprobado)

    def test_rechazar_solicitud(self):
        """Test rechazar solicitud"""
        self.solicitud.rechazar(observaciones="Fecha no disponible")
        self.assertEqual(self.solicitud.estado, 'CANCELADO')
        self.assertFalse(self.solicitud.puede_cancelar)


class SolicitudArriendoAPITests(APITestCase):
    def setUp(self):
        self.junta = JuntaVecinos.objects.create(
            nombre="Junta Test",
            direccion="Calle Test 123",
            sector="Sector Test"
        )
        
        # Usuario vecino
        self.vecino = User.objects.create_user(
            username='vecino',
            email='vecino@test.com',
            password='testpass123',
            rol='VECINO',
            estado='APROBADO',
            juntas_vecinos=self.junta
        )
        
        # Usuario tesorero
        self.tesorero = User.objects.create_user(
            username='tesorero',
            email='tesorero@test.com',
            password='testpass123',
            rol='TESORERO',
            estado='APROBADO',
            juntas_vecinos=self.junta
        )

    def test_crear_solicitud_como_vecino(self):
        """Test crear solicitud como vecino autenticado"""
        self.client.force_authenticate(user=self.vecino)
        
        data = {
            'fecha_evento': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'hora_inicio': '14:00:00',
            'hora_fin': '18:00:00',
            'motivo': 'Cumpleaños familiar',
            'cantidad_asistentes': 30
        }
        
        response = self.client.post('/api/arriendos/solicitudes/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SolicitudArriendo.objects.count(), 1)

    def test_crear_solicitud_fecha_pasada(self):
        """Test validación de fecha pasada"""
        self.client.force_authenticate(user=self.vecino)
        
        data = {
            'fecha_evento': (date.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'hora_inicio': '14:00:00',
            'hora_fin': '18:00:00',
            'motivo': 'Evento pasado',
            'cantidad_asistentes': 30
        }
        
        response = self.client.post('/api/arriendos/solicitudes/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_obtener_mis_solicitudes(self):
        """Test endpoint mis-solicitudes"""
        self.client.force_authenticate(user=self.vecino)
        
        # Crear una solicitud
        SolicitudArriendo.objects.create(
            solicitante=self.vecino,
            fecha_evento=date.today() + timedelta(days=7),
            hora_inicio=time(14, 0),
            hora_fin=time(18, 0),
            motivo="Test",
            cantidad_asistentes=50
        )
        
        response = self.client.get('/api/arriendos/solicitudes/mis-solicitudes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_aprobar_solicitud_como_tesorero(self):
        """Test aprobar solicitud como tesorero"""
        # Crear solicitud
        solicitud = SolicitudArriendo.objects.create(
            solicitante=self.vecino,
            fecha_evento=date.today() + timedelta(days=7),
            hora_inicio=time(14, 0),
            hora_fin=time(18, 0),
            motivo="Test",
            cantidad_asistentes=50
        )
        
        self.client.force_authenticate(user=self.tesorero)
        
        data = {
            'accion': 'APROBAR',
            'monto_pago': 50000,
            'observaciones': 'Aprobado por tesorero'
        }
        
        response = self.client.post(
            f'/api/arriendos/solicitudes/{solicitud.id}/aprobar/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, 'APROBADO')

    def test_subir_comprobante(self):
        """Test subir comprobante de pago"""
        # Crear solicitud aprobada
        solicitud = SolicitudArriendo.objects.create(
            solicitante=self.vecino,
            fecha_evento=date.today() + timedelta(days=7),
            hora_inicio=time(14, 0),
            hora_fin=time(18, 0),
            motivo="Test",
            cantidad_asistentes=50,
            estado='APROBADO',
            monto_pago=50000
        )
        
        self.client.force_authenticate(user=self.vecino)
        
        data = {
            'comprobante_pago_base64': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...'
        }
        
        response = self.client.post(
            f'/api/arriendos/solicitudes/{solicitud.id}/subir-comprobante/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        solicitud.refresh_from_db()
        self.assertTrue(solicitud.tiene_comprobante)

    def test_disponibilidad_endpoint(self):
        """Test endpoint de disponibilidad"""
        self.client.force_authenticate(user=self.vecino)
        
        # Crear una solicitud aprobada
        SolicitudArriendo.objects.create(
            solicitante=self.vecino,
            fecha_evento=date.today() + timedelta(days=7),
            hora_inicio=time(14, 0),
            hora_fin=time(18, 0),
            motivo="Test",
            cantidad_asistentes=50,
            estado='APROBADO'
        )
        
        fecha_consulta = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
        response = self.client.get(f'/api/arriendos/disponibilidad/?fecha={fecha_consulta}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['ocupados']), 1)
        self.assertIn('disponibles', response.data)

    def test_estadisticas_solo_admins(self):
        """Test que solo admins pueden ver estadísticas"""
        # Como vecino - debe fallar
        self.client.force_authenticate(user=self.vecino)
        response = self.client.get('/api/arriendos/estadisticas/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Como tesorero - debe funcionar
        self.client.force_authenticate(user=self.tesorero)
        response = self.client.get('/api/arriendos/estadisticas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('resumen', response.data)
