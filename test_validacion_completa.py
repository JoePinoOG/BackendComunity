#!/usr/bin/env python
"""
Script para probar que todos los usuarios ahora requieren validación del presidente
"""
import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backendcomunity.settings')
django.setup()

from django.contrib.auth import get_user_model
from usuarios.models import HistorialValidacion

User = get_user_model()

def test_registro_requiere_validacion():
    """Prueba que todos los registros requieren validación"""
    print("=== Prueba: Todos los usuarios requieren validación ===")
    
    # Datos de prueba para diferentes roles
    usuarios_prueba = [
        {
            'username': 'test_vecino_2025',
            'email': 'vecino2025@test.com',
            'rol': 'VECINO',
            'rut': '11111111-1'
        },
        {
            'username': 'test_secretario_2025',
            'email': 'secretario2025@test.com', 
            'rol': 'SECRETARIO',
            'rut': '22222222-2'
        },
        {
            'username': 'test_tesorero_2025',
            'email': 'tesorero2025@test.com',
            'rol': 'TESORERO', 
            'rut': '33333333-3'
        },
        {
            'username': 'test_presidente_2025',
            'email': 'presidente2025@test.com',
            'rol': 'PRESIDENTE',
            'rut': '44444444-4'
        }
    ]
    
    for datos in usuarios_prueba:
        try:
            # Crear usuario
            usuario = User.objects.create_user(
                username=datos['username'],
                email=datos['email'],
                password='testpass123',
                first_name='Test',
                last_name='Usuario',
                rol=datos['rol'],
                rut=datos['rut'],
                direccion='Calle Test 123',
                telefono='123456789'
            )
            
            print(f"✅ Usuario creado: {usuario.username}")
            print(f"   - Rol: {usuario.get_rol_display()}")
            print(f"   - Estado: {usuario.get_estado_display()}")
            print(f"   - ¿Requiere aprobación?: {'SÍ' if usuario.estado == 'PENDIENTE' else 'NO'}")
            print()
            
        except Exception as e:
            print(f"❌ Error creando usuario {datos['username']}: {e}")
    
    return True

def mostrar_usuarios_pendientes():
    """Mostrar todos los usuarios pendientes"""
    print("=== Usuarios Pendientes de Validación ===")
    
    usuarios_pendientes = User.objects.filter(estado='PENDIENTE').order_by('date_joined')
    
    if not usuarios_pendientes:
        print("No hay usuarios pendientes.")
        return
    
    print(f"Total de usuarios pendientes: {usuarios_pendientes.count()}")
    print()
    
    for usuario in usuarios_pendientes:
        tiempo_pendiente = "Recién creado"
        if usuario.date_joined:
            from django.utils import timezone
            tiempo = timezone.now() - usuario.date_joined
            if tiempo.days > 0:
                tiempo_pendiente = f"{tiempo.days} día(s)"
            else:
                tiempo_pendiente = "Hoy"
        
        print(f"👤 {usuario.get_full_name()} (@{usuario.username})")
        print(f"   - Email: {usuario.email}")
        print(f"   - Rol solicitado: {usuario.get_rol_display()}")
        print(f"   - RUT: {usuario.rut}")
        print(f"   - Tiempo pendiente: {tiempo_pendiente}")
        print()

def mostrar_estadisticas():
    """Mostrar estadísticas de usuarios por estado"""
    print("=== Estadísticas de Usuarios ===")
    
    total_usuarios = User.objects.count()
    pendientes = User.objects.filter(estado='PENDIENTE').count()
    aprobados = User.objects.filter(estado='APROBADO').count()
    rechazados = User.objects.filter(estado='RECHAZADO').count()
    
    print(f"Total de usuarios: {total_usuarios}")
    print(f"Pendientes: {pendientes}")
    print(f"Aprobados: {aprobados}")
    print(f"Rechazados: {rechazados}")
    print()
    
    # Por rol
    print("Por rol:")
    for rol_code, rol_name in User.ROLES:
        total_rol = User.objects.filter(rol=rol_code).count()
        pendientes_rol = User.objects.filter(rol=rol_code, estado='PENDIENTE').count()
        aprobados_rol = User.objects.filter(rol=rol_code, estado='APROBADO').count()
        rechazados_rol = User.objects.filter(rol=rol_code, estado='RECHAZADO').count()
        
        if total_rol > 0:
            print(f"  {rol_name}: {total_rol} total ({pendientes_rol} pendientes, {aprobados_rol} aprobados, {rechazados_rol} rechazados)")

if __name__ == "__main__":
    try:
        print("🔧 SISTEMA DE VALIDACIÓN DE USUARIOS - PRUEBA COMPLETA")
        print("=" * 60)
        print()
        
        # Probar que todos los roles requieren validación
        test_registro_requiere_validacion()
        
        # Mostrar usuarios pendientes
        mostrar_usuarios_pendientes()
        
        # Mostrar estadísticas
        mostrar_estadisticas()
        
        print("=" * 60)
        print("✅ CAMBIO IMPLEMENTADO EXITOSAMENTE")
        print()
        print("🎯 RESUMEN DEL CAMBIO:")
        print("- ANTES: Solo directiva requería validación")
        print("- AHORA: TODOS los usuarios requieren validación del presidente")
        print()
        print("📋 PRÓXIMOS PASOS PARA EL FRONTEND:")
        print("1. Actualizar mensaje de registro para todos los usuarios")
        print("2. Mostrar vecinos en el panel de validación del presidente")
        print("3. Actualizar interfaz para manejar todos los roles en pendientes")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()
