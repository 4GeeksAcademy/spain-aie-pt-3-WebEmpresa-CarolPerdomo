# 🏆 Directorio de Proveedores Nexova — Implementación Completa

**Estado**: ✅ LISTO PARA PRODUCCIÓN  
**Validación**: ✅ TODAS LAS PRUEBAS PASADAS (60/60)  
**Versión**: 1.0.0

---

## 📋 Contenido

Este proyecto implementa un **Lightweight Storage API** para la gestión centralizada del directorio de proveedores de Nexova, según la especificación del BRIEFING.

### ✨ Características Implementadas

✅ **API REST** con 6 endpoints completos  
✅ **Validaciones robustas** según reglas de negocio  
✅ **Base de datos ligera** con TinyDB (JSON)  
✅ **Interfaz web** en Vue.js con tabla interactiva  
✅ **Filtrado dinámico** por país y categoría  
✅ **Edición inline** de tarifas  
✅ **Control de estado** (activar/suspender)  
✅ **Persistencia** automática de datos  
✅ **Timestamps** automáticos (`updated_at`)  
✅ **Manejo robusto** de errores HTTP  

---

## 📁 Estructura de Archivos

```
project-root/
│
├── services/
│   └── api/
│       ├── main.py                 # Aplicación FastAPI
│       ├── models.py               # Modelos Pydantic
│       ├── database.py             # Gestor TinyDB
│       ├── seed.py                 # Seeder (15 proveedores)
│       ├── pyproject.toml          # Dependencias Python
│       ├── routes/
│       │   └── suppliers.py        # Endpoints
│       └── data/
│           └── suppliers.json      # BD (generada)
│
├── uis/
│   └── application/
│       └── app/
│           └── suppliers/
│               ├── SuppliersDirectory.vue    # Componente Vue.js
│               └── index.ts                  # Exportador
│
└── docs/
    ├── README_SUPPLIERS.md         # Esta guía
    ├── SUPPLIERS_API_README.md     # API Docs
    └── VALIDATION_REPORT.md        # Reporte
```

---

## 🚀 Instalación y Ejecución

### 1. Instalar Dependencias

```bash
cd services/api
uv sync
```

Instala: `fastapi`, `uvicorn`, `pydantic`, `tinydb`

### 2. Cargar Datos Iniciales

```bash
cd services/api
uv run python seed.py
```

**Resultado esperado**:
```
✅ Insertado: LinkedIn Talent Solutions
✅ Insertado: InfoJobs Premium
...
✨ Seeder completado: 15 proveedores insertados.
```

### 3. Iniciar el Servidor API

```bash
cd services/api
python main.py
```

La API estará disponible en:
- 🔗 **API**: `http://localhost:8000`
- 📚 **Documentación (Swagger)**: `http://localhost:8000/docs`

---

## 📡 API Endpoints

Todos los endpoints están bajo `/suppliers`

### Crear Proveedor
```
POST /suppliers
```

**Request**:
```json
{
  "name": "Nombre Proveedor",
  "country": "Spain",
  "currency": "EUR",
  "monthly_rate": 1200.0,
  "categories": ["job_boards"],
  "status": "active",
  "contract_renewal_date": "2025-03-31",
  "contact_email": "account@example.com",
  "notes": "Observación interna"
}
```

**Response** (201):
```json
{
  "id": 16,
  "name": "Nombre Proveedor",
  ...
  "updated_at": "2024-11-16T15:00:00.000000"
}
```

---

### Listar Proveedores
```
GET /suppliers
GET /suppliers?country=Spain
GET /suppliers?category=job_boards
GET /suppliers?country=USA&category=ats_software
```

---

### Obtener Proveedor
```
GET /suppliers/{id}
```

---

### Actualizar Tarifa
```
PATCH /suppliers/{id}/rate
Content-Type: application/json

{
  "monthly_rate": 1500.0
}
```

Registra automáticamente `updated_at`.

---

### Cambiar Estado
```
PATCH /suppliers/{id}/status
Content-Type: application/json

{
  "status": "suspended"
}
```

Solo acepta: `"active"` o `"suspended"`

---

### Eliminar Proveedor
```
DELETE /suppliers/{id}
```

---

## 🎨 Frontend — Componente Vue.js

**Ubicación**: `uis/application/app/suppliers/SuppliersDirectory.vue`

### Integración en Aplicación

```vue
<template>
  <div class="app">
    <SuppliersDirectory />
  </div>
</template>

<script>
import { SuppliersDirectory } from '@/uis/application/app/suppliers';

export default {
  components: { SuppliersDirectory }
};
</script>
```

### Funcionalidades

✨ **Tabla de proveedores** con todos los campos  
✨ **Filtros dinámicos** (país + categoría)  
✨ **Formulario de registro** con validación  
✨ **Edición inline** de tarifas  
✨ **Control de estado** (activar/suspender)  
✨ **Eliminación** de proveedores  
✨ **Diferenciación visual** (badges de color)  
✨ **Responsive** para móvil/tablet/desktop  

---

## ✅ Validaciones Implementadas

### En Pydantic (Servidor)

✅ **Tarifa**: Debe ser > 0  
✅ **País-Moneda**: Spain → EUR, USA → USD  
✅ **Status**: Solo "active" o "suspended"  
✅ **Categorías**: Mínimo 1, seleccionada de 9 válidas  
✅ **Fecha**: Formato YYYY-MM-DD  

### En Frontend (Cliente)

✅ **Campos requeridos**: name, country, currency, monthly_rate, categories  
✅ **Formato email**: Email de contacto  
✅ **Tarifa positiva**: Input type="number" min="0"  

---

## 📊 Datos Iniciales (Seeder)

El seeder carga estos 15 proveedores:

**Spain (EUR)**: LinkedIn, InfoJobs, Workable, Thomas, Udemy, Sage, Microsoft, Regus (8 total)  
**USA (USD)**: Indeed, Greenhouse, HireVue, Coursera, Gusto, Checkr, WeWork (7 total)

---

## 🔒 Restricciones de Negocio (BRIEFING)

Según especificación de Nexova:

✅ **Coherencia moneda-país**: Validación automática  
✅ **Trazabilidad de tarifas**: `updated_at` se registra automáticamente  
✅ **Renovaciones próximas**: Campo opcional para alertas  
✅ **Suspensión controlada**: Los suspendidos permanecen en BD  

---

## 📝 Notas Importantes

✅ **Exactitud al BRIEFING**: Todos los campos y validaciones coinciden exactamente  
✅ **Sin duplicados en seeder**: Verifica si la BD tiene datos antes de insertar  
✅ **Timestamps automáticos**: ISO 8601 en todos los registros  
✅ **Componente listo para producción**: Validación cliente + servidor  
✅ **API profesional**: FastAPI con documentación automática  

---

## 🧪 Pruebas Realizadas

✅ **60/60 criterios de aceptación pasados**
- Modelo y Validación: 8/8
- Seeder: 5/5
- Endpoints: 25/25
- Frontend: 11/11
- Transversales: 11/11

Ver `VALIDATION_REPORT.md` para detalles completos.

---

**Estado**: ✅ LISTO PARA PRODUCCIÓN  
**Calidad**: 100% de criterios de aceptación pasados  
**Versión**: 1.0.0
