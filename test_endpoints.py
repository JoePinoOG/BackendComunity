import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
HEADERS = {
    'Content-Type': 'application/json',
    # Agrega tu token JWT aquí cuando tengas uno
    # 'Authorization': 'Bearer YOUR_TOKEN_HERE'
}

def test_endpoints():
    print("🔍 Probando endpoints de certificados...")
    
    # 1. Probar endpoint de configuración
    print("\n1. Probando configuración del certificado:")
    try:
        response = requests.get(f"{BASE_URL}/api/documentos/certificado/config/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Config: {response.json()}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 2. Probar endpoint de solicitud (necesita autenticación)
    print("\n2. Probando solicitud de certificado:")
    try:
        response = requests.post(
            f"{BASE_URL}/api/documentos/certificado/solicitar/",
            headers=HEADERS,
            json={
                "nombre_completo": "Juan Pérez Test",
                "cedula_identidad": "12345678-9",
                "domicilio_completo": "Calle Test 123",
                "institucion_destino": "Empresa Test"
            }
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ⚠️  Necesita autenticación (esperado)")
        elif response.status_code == 201:
            print(f"   ✅ Certificado creado: {response.json()}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 3. Probar endpoint de lista de certificados
    print("\n3. Probando lista de certificados:")
    try:
        response = requests.get(f"{BASE_URL}/api/documentos/certificado/mis-solicitudes/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ⚠️  Necesita autenticación (esperado)")
        elif response.status_code == 200:
            print(f"   ✅ Lista obtenida: {response.json()}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 4. Probar endpoint de descarga (ejemplo)
    print("\n4. Probando descarga de certificado:")
    try:
        response = requests.get(f"{BASE_URL}/api/documentos/certificado/1/descargar/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ⚠️  Necesita autenticación (esperado)")
        elif response.status_code == 404:
            print("   ⚠️  Certificado no encontrado (esperado)")
        elif response.status_code == 200:
            print("   ✅ Descarga exitosa")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_endpoints()
