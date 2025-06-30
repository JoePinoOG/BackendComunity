"""
Script para probar los endpoints de reuniones
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

def test_endpoints():
    print("🔍 Probando endpoints de reuniones...")
    
    # 1. Probar endpoint de obtener token (LOGIN)
    print("\n1. Probando login...")
    login_data = {
        "username": "admin",  # Cambiar por credenciales válidas
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{API_URL}/token/", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access')
            headers = {'Authorization': f'Bearer {token}'}
            
            # 2. Probar GET de reuniones
            print("\n2. Probando GET reuniones...")
            response = requests.get(f"{API_URL}/reuniones/reuniones/", headers=headers)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # 3. Probar POST de reuniones
            print("\n3. Probando POST reuniones...")
            reunion_data = {
                "motivo": "ORDINARIA",
                "fecha": "2025-07-15T10:00:00Z",
                "lugar": "Sala de reuniones",
                "descripcion": "Reunión de prueba",
                "participantes": []
            }
            
            response = requests.post(f"{API_URL}/reuniones/reuniones/", 
                                   json=reunion_data, headers=headers)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
        else:
            print(f"   Error en login: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor. ¿Está ejecutándose?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoints()
