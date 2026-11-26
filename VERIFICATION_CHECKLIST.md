# ✅ SUPPLIER MANAGEMENT SYSTEM — VERIFICATION CHECKLIST

**Timestamp:** 2026-11-14 14:59:21 UTC  
**Repository:** spain-aie-pt-3-WebEmpresa-CarolPerdomo  
**Status:** VERIFICATION IN PROGRESS

---

## 📋 CRITERIOS DE ACEPTACIÓN

### 1️⃣ MODELO Y VALIDACIÓN

- [ ] **1.1** Modelo Pydantic refleja exactamente campos del BRIEFING
  - name ✓
  - country (spain) ✓
  - categories (5 tipos) ✓
  - daily_rate ✓
  - status (active/inactive) ✓
  - updated_at ✓

- [ ] **1.2** Status fuera del conjunto permitido → 422
  - Valid: active, inactive
  - Test: POST /suppliers con status invalido

- [ ] **1.3** Tarifa ≤ 0 → rechazado con 422
  - daily_rate > 0 obligatorio
  - Test: POST /suppliers con daily_rate=0 o negativo

- [ ] **1.4** `updated_at` generado por sistema (no enviado por cliente)
  - No incluye en SupplierCreate
  - Se genera en db.py en cada operación

### 2️⃣ SEEDER

- [ ] **2.1** `uv run seed` se ejecuta sin errores
- [ ] **2.2** Carga proveedores del BRIEFING (5 proveedores)
- [ ] **2.3** Ejecución repetida NO produce duplicados
- [ ] **2.4** Confirma número de registros insertados en consola

### 3️⃣ ENDPOINTS

- [ ] **3.1** POST /suppliers
  - Crea proveedor
  - Devuelve objeto completo con ID
  - Rechaza entradas inválidas con 422

- [ ] **3.2** GET /suppliers
  - Sin parámetros: devuelve TODOS
  - ?country=x: devuelve solo país x
  - ?category=y: devuelve solo categoría y

- [ ] **3.3** GET /suppliers/{id}
  - Devuelve detalle con id válido
  - Devuelve 404 con id inexistente

- [ ] **3.4** PATCH /suppliers/{id}/rate
  - Actualiza daily_rate
  - Registra timestamp updated_at
  - Rechaza rate ≤ 0 con 422

- [ ] **3.5** PATCH /suppliers/{id}/status
  - Rechaza valores no permitidos con 422
  - Solo acepta: active, inactive

- [ ] **3.6** DELETE /suppliers/{id}
  - Elimina con id válido (204)
  - Devuelve 404 con id inexistente

### 4️⃣ FRONTEND

- [ ] **4.1** Listado carga desde API
  - Muestra campos del BRIEFING
  - Tabla rendida correctamente

- [ ] **4.2** Filtros funcionan sin reload
  - Country filter
  - Category filter
  - Actualiza listado en tiempo real

- [ ] **4.3** Formulario de registro
  - Valida en cliente campos requeridos
  - Muestra error de API si rechaza entrada

- [ ] **4.4** Actualización de tarifa reflejada
  - Cambio visible inmediatamente
  - Llamada a PATCH correcta

- [ ] **4.5** Cambio de estado reflejado
  - Dropdown/toggle funciona
  - Cambio visible inmediatamente

- [ ] **4.6** Diferenciación visual
  - Activos vs suspendidos visibles
  - Badge, color o estilo diferenciado

### 5️⃣ TRANSVERSALES

- [ ] **5.1** TinyDB persiste correctamente
  - Datos persisten tras reiniciar servidor
  - db.json existe en disco

- [ ] **5.2** Códigos HTTP correctos
  - 404 cuando no se encuentran recursos
  - 422 cuando entrada es inválida
  - 200/201 cuando operación es exitosa
  - 204 en DELETE exitoso

- [ ] **5.3** Estructura de carpetas correcta
  - services/supplier_management/ (backend)
  - uis/backoffice/ (frontend)

---

## 🧪 TESTS EJECUTADOS

### Backend Tests (Python)
- [ ] Models validation
- [ ] Enum enforcement (status, categories)
- [ ] Rate validation (positive numbers)
- [ ] Timestamp generation
- [ ] Database operations
- [ ] All 7 endpoints

### Manual Tests (curl)
- [ ] POST /suppliers (valid data)
- [ ] POST /suppliers (invalid status)
- [ ] POST /suppliers (zero/negative rate)
- [ ] GET /suppliers (no params)
- [ ] GET /suppliers?country=spain
- [ ] GET /suppliers?category=Software
- [ ] GET /suppliers/{id} (valid id)
- [ ] GET /suppliers/{id} (invalid id)
- [ ] PATCH /suppliers/{id}/rate (valid)
- [ ] PATCH /suppliers/{id}/rate (invalid)
- [ ] PATCH /suppliers/{id}/status (valid)
- [ ] PATCH /suppliers/{id}/status (invalid)
- [ ] DELETE /suppliers/{id} (valid)
- [ ] DELETE /suppliers/{id} (invalid)

### Seeder Tests
- [ ] First run: inserta 5 registros
- [ ] Second run: no duplica

### Frontend Tests
- [ ] Page loads
- [ ] Table renders
- [ ] Filters work
- [ ] Form submits
- [ ] Rate update works
- [ ] Status toggle works

### Persistencia
- [ ] DB data survives server restart

---

## 📊 RESULTS SUMMARY

**Total Criteria:** 40+  
**Passed:** 0  
**Failed:** 0  
**Pending:** 0  

---

## 🚀 NEXT STEPS

1. Start backend server
2. Run seeder
3. Execute all endpoint tests (curl)
4. Start frontend
5. Test UI interactions
6. Test persistence (restart + verify)
7. Mark all as PASS/FAIL

