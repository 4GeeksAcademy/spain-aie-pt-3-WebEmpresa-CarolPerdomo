# 📋 Nexova Suppliers Directory - Lightweight Storage API

API y interfaz de gestión para el directorio centralizado de proveedores de Nexova.

## 🎯 Características

✅ Gestión completa de proveedores  
✅ Validación automática según reglas de negocio  
✅ Almacenamiento ligero con TinyDB  
✅ API REST con FastAPI  
✅ Frontend interactivo en Vue.js  
✅ Filtrado por país y categoría  
✅ Actualización de tarifas en tiempo real  
✅ Control de estado (activo/suspendido)  

## 📁 Estructura

```
.
├── suppliers_model.py        # Modelos Pydantic
├── db_suppliers.py           # Base de datos TinyDB
├── api_suppliers.py          # Endpoints FastAPI
├── seed.py                   # Seeder de datos iniciales
├── data/
│   └── suppliers.json        # Base de datos (generada)
└── uis/backoffice/
    └── SuppliersDirectory.vue # Componente Vue
```

## 🚀 Instalación y Ejecución

### Backend

1. **Instalar dependencias** (con `uv`):
```bash
uv sync
```

2. **Ejecutar seeder** (carga datos iniciales):
```bash
uv run seed
```

3. **Iniciar API**:
```bash
uv run python api_suppliers.py
```

La API estará disponible en `http://localhost:8000`  
Documentación interactiva: `http://localhost:8000/docs`

### Frontend

Integra el componente Vue `SuppliersDirectory.vue` en tu aplicación de backoffice.

```vue
<template>
  <SuppliersDirectory />
</template>

<script>
import SuppliersDirectory from '@/uis/backoffice/SuppliersDirectory.vue';

export default {
  components: { SuppliersDirectory }
};
</script>
```

## 📊 Endpoints API

### Crear Proveedor
```
POST /suppliers
Content-Type: application/json

{
  "name": "Nombre Proveedor",
  "country": "Spain",
  "currency": "EUR",
  "monthly_rate": 1200.0,
  "categories": ["job_boards"],
  "status": "active",
  "contract_renewal_date": "2025-03-31",
  "contact_email": "account@supplier.com",
  "notes": "Observación interna"
}
```

**Respuesta (201)**:
```json
{
  "id": 1,
  "name": "Nombre Proveedor",
  "country": "Spain",
  "currency": "EUR",
  "monthly_rate": 1200.0,
  "categories": ["job_boards"],
  "status": "active",
  "contract_renewal_date": "2025-03-31",
  "contact_email": "account@supplier.com",
  "notes": "Observación interna",
  "updated_at": "2024-11-16T14:54:00"
}
```

### Listar Proveedores
```
GET /suppliers?country=Spain&category=job_boards
```

Parámetros opcionales:
- `country`: `Spain` o `USA`
- `category`: Una de las 9 categorías válidas

**Respuesta (200)**:
```json
[
  {
    "id": 1,
    "name": "LinkedIn Talent Solutions",
    "country": "Spain",
    ...
  }
]
```

### Obtener Proveedor
```
GET /suppliers/{id}
```

### Actualizar Tarifa
```
PATCH /suppliers/{id}/rate
Content-Type: application/json

{
  "monthly_rate": 1500.0
}
```

Registra automáticamente `updated_at`.

### Cambiar Estado
```
PATCH /suppliers/{id}/status
Content-Type: application/json

{
  "status": "suspended"
}
```

Solo acepta: `"active"` o `"suspended"`

### Eliminar Proveedor
```
DELETE /suppliers/{id}
```

## ✅ Validaciones Implementadas

- **Tarifa**: Debe ser mayor a 0
- **País + Moneda**: Spain → EUR, USA → USD
- **Estado**: Solo "active" o "suspended"
- **Categorías**: Mínimo 1, seleccionada de 9 opciones válidas
- **Formato de fecha**: YYYY-MM-DD para `contract_renewal_date`

## 🗄️ Datos Iniciales

El seeder carga automáticamente 15 proveedores de Nexova:

- **Spain (EUR)**: LinkedIn, InfoJobs, Workable, Thomas, Udemy, Sage, Microsoft 365, Regus
- **USA (USD)**: Indeed, Greenhouse, HireVue, Coursera, Gusto, Checkr, WeWork

Ejecuta `uv run seed` para cargarlos.

## 🎨 Interfaz de Usuario

La página de directorio de proveedores (`SuppliersDirectory.vue`) incluye:

✨ **Filtrado dinámico** por país y categoría  
✨ **Formulario de registro** con validación  
✨ **Edición inline** de tarifas  
✨ **Control de estado** (activar/suspender)  
✨ **Eliminación** de proveedores  
✨ **Diferenciación visual** (activo/suspendido)  
✨ **Responsive** para móvil y escritorio  

## 🔒 Restricciones de Negocio

Según el BRIEFING de Nexova:

1. **Moneda por país**: Coherencia automática validada
2. **Trazabilidad**: `updated_at` se registra automáticamente en cambios de tarifa
3. **Renovaciones**: Campo opcional, útil para alertas de próximas renovaciones
4. **Suspensión**: Los proveedores suspendidos permanecen en el directorio (no se eliminan)

## 📝 Notas

- La base de datos TinyDB se almacena en `data/suppliers.json`
- El seeder verifica duplicados antes de insertar
- El frontend consume los endpoints en `http://localhost:8000`
- Todos los timestamps están en ISO 8601

---

**Documento interno — Nexova AI Engineering · 4Geeks Academy**
