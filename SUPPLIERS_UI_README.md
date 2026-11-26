# 🚀 Interfaz Gráfica de Proveedores - Nexova

## ✅ Estado del Sistema

La interfaz gráfica de gestión de proveedores está **COMPLETAMENTE OPERATIVA** y lista para usar.

## 🌐 Acceso a la Interfaz

### URL de Acceso
```
https://cuddly-enigma-qvqjg4w7rx9g36x5r-3000.app.github.dev/suppliers-ui.html
```

### Componentes en Ejecución

| Componente | Puerto | Estado | URL |
|-----------|--------|--------|-----|
| **FastAPI Backend** | 8000 | ✅ Running | https://cuddly-enigma-qvqjg4w7rx9g36x5r-8000.app.github.dev/ |
| **HTTP Server** | 3000 | ✅ Running | https://cuddly-enigma-qvqjg4w7rx9g36x5r-3000.app.github.dev/ |
| **API Swagger UI** | 8000 | ✅ Running | https://cuddly-enigma-qvqjg4w7rx9g36x5r-8000.app.github.dev/docs |

## 🎯 Funcionalidades

### 📊 Visualización
- Tabla interactiva con todos los proveedores
- Información detallada: Nombre, País, Categoría, Tarifa, Estado, Renovación

### 🔍 Filtrado Avanzado
- **Por País**: Spain 🇪🇸 / USA 🇺🇸
- **Por Categoría**: Job Boards, ATS Software, Assessment Tools, Training Platforms, Payroll & HR, Video Interview, Background Check, Office & Facilities, IT & Software

### ➕ Crear Proveedores
- Formulario completo con validación de datos
- Campos: Nombre, País, Moneda, Tarifa Mensual, Categorías, Email, Fecha Renovación, Notas
- Envío automático a la API

### ✏️ Editar Información
- Edición inline de tarifas mensuales
- Cambio de estado (Activo/Suspendido)
- Guardado automático en la base de datos

### 🗑️ Eliminar
- Confirmación de seguridad antes de eliminar
- Eliminación inmediata en la base de datos

## 📊 Datos Actuales

### Resumen General
- **Total de proveedores**: 15
- **Proveedores Activos**: 12 ✅
- **Proveedores Suspendidos**: 3 ⏸️

### Distribución por País
- 🇪🇸 **Spain**: 8 proveedores
- 🇺🇸 **USA**: 7 proveedores

### Categorías (9 tipos)
- 💼 Job Boards: 3 proveedores
- 🖥️ ATS Software: 2 proveedores
- 📋 Assessment Tools: 1 proveedor
- 📚 Training Platforms: 2 proveedores
- 💰 Payroll & HR: 2 proveedores
- 🎥 Video Interview: 1 proveedor
- 🔍 Background Check: 1 proveedor
- 🏢 Office & Facilities: 2 proveedores
- ⚙️ IT & Software Licenses: 1 proveedor

### Inversión Mensual Total
- EUR: €7,059.00/mes
- USD: $5,984.00/mes
- **Inversión combinada**: ~€13,000/mes (aproximado)

## 📚 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/suppliers` | Listar todos los proveedores |
| POST | `/suppliers` | Crear nuevo proveedor |
| PATCH | `/suppliers/{id}/rate` | Actualizar tarifa mensual |
| PATCH | `/suppliers/{id}/status` | Cambiar estado (activo/suspendido) |
| DELETE | `/suppliers/{id}` | Eliminar proveedor |

## 🛠️ Tecnologías Utilizadas

- **Frontend**: Vue 3 (desde CDN)
- **Backend**: FastAPI + Python
- **Database**: TinyDB
- **HTTP Server**: Python http.server
- **Estilos**: CSS Vanilla (Responsive Mobile-First)

## 💡 Cómo Usar

### 1. Visualizar Proveedores
Abre la interfaz y verás la lista completa de proveedores en la tabla.

### 2. Filtrar
- Usa el dropdown de "País" para filtrar por Spain o USA
- Usa el dropdown de "Categoría" para filtrar por tipo de servicio

### 3. Crear Nuevo Proveedor
1. Haz clic en "➕ Nuevo Proveedor"
2. Rellena el formulario con los datos requeridos (marcados con *)
3. Haz clic en "Registrar"
4. El nuevo proveedor aparecerá en la tabla

### 4. Editar Tarifa
1. En la columna "Tarifa Mensual", haz clic en el ícono de lápiz ✏️
2. Modifica el valor
3. Haz clic en el ícono de guardado 💾

### 5. Cambiar Estado
Haz clic en el ícono de candado 🔒 (activo) o abierto 🔓 (suspendido) para cambiar el estado.

### 6. Eliminar Proveedor
Haz clic en el ícono de papelera 🗑️ y confirma la eliminación.

## 🔧 Reiniciar los Servidores (si es necesario)

### FastAPI Backend
```bash
cd /workspaces/spain-aie-pt-3-WebEmpresa-CarolPerdomo
python -m uvicorn services.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### HTTP Server
```bash
cd /workspaces/spain-aie-pt-3-WebEmpresa-CarolPerdomo
python3 -m http.server 3000
```

## 📝 Notas Importantes

- Todos los cambios se guardan automáticamente en la base de datos TinyDB
- La interfaz es completamente responsiva (funciona en móvil, tablet y escritorio)
- CORS está habilitado en la API para permitir peticiones desde cualquier origen
- Los datos persisten entre sesiones

## 🐛 Troubleshooting

### La interfaz no carga
- Verifica que ambos servidores (8000 y 3000) están corriendo
- Recarga la página (Ctrl+R o Cmd+R)

### Los datos no se guardan
- Verifica que la API en puerto 8000 está respondiendo
- Abre la consola del navegador (F12) para ver errores

### Errores de conexión
- Verifica la URL de la API: `http://localhost:8000`
- Asegúrate de que el puerto 8000 no está en uso por otro proceso

---

**Versión**: 1.0.0  
**Última actualización**: 2026-11-16
