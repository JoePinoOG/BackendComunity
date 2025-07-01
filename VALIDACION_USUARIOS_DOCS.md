# Sistema de Validación de Usuarios - Documentación

## Descripción General

El sistema de validación de usuarios permite que el presidente de la junta de vecinos apruebe o rechace las solicitudes de registro de usuarios que quieren roles de directiva (Secretario, Tesorero, Presidente).

## Estados de Usuario

Los usuarios pueden tener los siguientes estados:
- **PENDIENTE**: Usuario registrado pero esperando aprobación
- **APROBADO**: Usuario aprobado y puede usar el sistema
- **RECHAZADO**: Usuario rechazado por el presidente

## Flujo de Registro

### 1. Registro de Vecinos
- Los usuarios que se registran con rol **VECINO** son aprobados automáticamente
- No requieren validación del presidente

### 2. Registro de Directiva
- Los usuarios que se registran con roles de **SECRETARIO**, **TESORERO** o **PRESIDENTE** quedan en estado **PENDIENTE**
- Requieren aprobación del presidente antes de poder usar el sistema

## Endpoints del API

### Registro de Usuario
```
POST /api/auth/usuarios/registro/
```

**Datos de entrada:**
```json
{
    "username": "usuario_ejemplo",
    "email": "usuario@ejemplo.com",
    "password": "contraseña123",
    "password_confirm": "contraseña123",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "rol": "SECRETARIO",
    "rut": "12345678-9",
    "direccion": "Calle Ejemplo 123",
    "telefono": "123456789"
}
```

**Respuesta para rol de directiva:**
```json
{
    "mensaje": "Registro exitoso. Tu solicitud está pendiente de aprobación por el presidente.",
    "require_approval": true,
    "usuario_id": 123,
    "estado": "PENDIENTE"
}
```

**Respuesta para vecino:**
```json
{
    "mensaje": "Registro exitoso. Tu cuenta ha sido aprobada automáticamente.",
    "require_approval": false,
    "usuario_id": 124,
    "estado": "APROBADO"
}
```

### Ver Usuarios Pendientes (Solo Presidente)
```
GET /api/auth/usuarios/usuarios_pendientes/
```

**Respuesta:**
```json
{
    "usuarios_pendientes": [
        {
            "id": 123,
            "username": "secretario_ejemplo",
            "email": "secretario@ejemplo.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "rol": "SECRETARIO",
            "direccion": "Calle Ejemplo 123",
            "telefono": "123456789",
            "rut": "12345678-9",
            "estado": "PENDIENTE",
            "date_joined": "2025-07-01T15:30:00Z",
            "tiempo_pendiente": "2 días"
        }
    ],
    "total": 1
}
```

### Validar Usuario (Solo Presidente)
```
POST /api/auth/usuarios/{id}/validar_usuario/
```

**Datos de entrada:**
```json
{
    "accion": "APROBAR",
    "observacion": "Usuario aprobado para el rol de secretario"
}
```

**Opciones para acción:**
- `"APROBAR"`: Aprobar al usuario
- `"RECHAZAR"`: Rechazar al usuario

**Respuesta:**
```json
{
    "mensaje": "Usuario Juan Pérez aprobado exitosamente",
    "usuario": {
        "id": 123,
        "username": "secretario_ejemplo",
        "estado": "APROBADO",
        ...
    },
    "observacion": "Usuario aprobado para el rol de secretario"
}
```

### Estadísticas de Validación (Solo Presidente)
```
GET /api/auth/usuarios/estadisticas_validacion/
```

**Respuesta:**
```json
{
    "pendientes": 3,
    "aprobados": 25,
    "rechazados": 2,
    "total": 30,
    "por_rol": {
        "VECINO": {
            "nombre": "Vecino",
            "total": 20,
            "pendientes": 0,
            "aprobados": 20,
            "rechazados": 0
        },
        "SECRETARIO": {
            "nombre": "Secretario",
            "total": 5,
            "pendientes": 2,
            "aprobados": 2,
            "rechazados": 1
        },
        ...
    }
}
```

### Historial de Validaciones (Solo Presidente)
```
GET /api/auth/usuarios/historial_validaciones/
```

**Respuesta:**
```json
{
    "historial": [
        {
            "id": 1,
            "usuario_validado": {
                "id": 123,
                "username": "secretario_ejemplo",
                "nombre_completo": "Juan Pérez",
                "rol": "Secretario"
            },
            "validado_por": {
                "id": 1,
                "username": "presidente",
                "nombre_completo": "María García"
            },
            "accion": "APROBADO",
            "observacion": "Usuario aprobado para el rol de secretario",
            "fecha_validacion": "2025-07-01T16:00:00Z"
        }
    ],
    "total_registros": 15
}
```

## Permisos y Seguridad

### Permisos Implementados
- **EsPresidente**: Solo usuarios con rol PRESIDENTE
- **PuedeValidarUsuarios**: Solo presidentes pueden validar usuarios
- **PuedeVerUsuariosPendientes**: Solo presidentes pueden ver usuarios pendientes

### Restricciones de Seguridad
1. Un presidente no puede validarse a sí mismo
2. Solo se pueden validar usuarios en estado PENDIENTE
3. Solo usuarios con roles de directiva requieren validación
4. El historial de validaciones es de solo lectura

## Uso en el Frontend

### 1. Página de Registro
```javascript
// Ejemplo de manejo del registro
const registrarUsuario = async (userData) => {
    try {
        const response = await fetch('/api/auth/usuarios/registro/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (data.require_approval) {
            // Mostrar mensaje de que debe esperar aprobación
            mostrarMensaje('Tu solicitud está pendiente de aprobación por el presidente.');
        } else {
            // Redirigir al login o dashboard
            mostrarMensaje('Registro exitoso. Puedes iniciar sesión.');
        }
    } catch (error) {
        console.error('Error en registro:', error);
    }
};
```

### 2. Panel de Administración (Solo Presidente)
```javascript
// Obtener usuarios pendientes
const obtenerUsuariosPendientes = async () => {
    const response = await fetch('/api/auth/usuarios/usuarios_pendientes/', {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
    return response.json();
};

// Validar usuario
const validarUsuario = async (usuarioId, accion, observacion = '') => {
    const response = await fetch(`/api/auth/usuarios/${usuarioId}/validar_usuario/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
            accion: accion,
            observacion: observacion
        })
    });
    return response.json();
};
```

## Consideraciones Adicionales

1. **Primer Presidente**: El primer usuario con rol PRESIDENTE debe ser creado manualmente por un administrador o através del admin de Django.

2. **Notificaciones**: Se puede implementar un sistema de notificaciones por email cuando un usuario es aprobado o rechazado.

3. **Logs**: Todas las validaciones quedan registradas en el modelo `HistorialValidacion` para auditoría.

4. **Escalabilidad**: El sistema está diseñado para manejar múltiples juntas de vecinos si se implementa esa funcionalidad en el futuro.
