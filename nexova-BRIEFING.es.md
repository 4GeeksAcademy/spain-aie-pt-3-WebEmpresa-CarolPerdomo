# BRIEFING — Utilidad de Análisis de Datos: Procesador de Reportes de Incidentes

## Empresa: Nexova

---

## Tu empresa

**Nexova** es una firma de consultoría y outsourcing de recursos humanos con sede en Valencia, España, y una oficina en Miami. Entre sus líneas de negocio, Nexova opera un **servicio de outsourcing de soporte al cliente**: 30 agentes gestionan incidentes para clientes de Nexova (tecnología, retail y finanzas) por teléfono, correo electrónico y chat web.

Formas parte del equipo de **Nexova AI Engineering**, bajo la dirección de **Sergio Molina (CTO)**. Tu contacto para este proyecto es **Roberto Díaz (Customer Support Lead)**.

El equipo de Roberto utiliza un helpdesk legado para registrar cada ticket de soporte recibido. Se exportó un mes de datos en CSV para su análisis y tu archivo de prueba tiene **1,000 filas**. El SLA promedio comprometido con clientes es de **24 horas**; actualmente el promedio está en 48 horas. Roberto necesita este análisis para entender el backlog de tickets y las brechas de satisfacción antes de la próxima revisión con clientes.

El objetivo de tu script es dar a Roberto y a los supervisores una visión clara y precisa de los datos de tickets, sin enviar información a herramientas de IA externas.

---

## Estructura del CSV

**Nombre de archivo:** `incidents.csv`  
**Codificación:** UTF-8  
**Separador:** coma (`,`)  
**Fila de encabezado:** sí (fila 1)

| Campo                | Tipo    | Requerido | Valores permitidos / formato                        |
| -------------------- | ------- | --------- | --------------------------------------------------- |
| `ticket_id`          | string  | ✅        | ID único, formato `NXV-XXXXXX` (ej.: `NXV-000001`)  |
| `date`               | string  | ✅        | `YYYY-MM-DD`                                        |
| `client_company`     | string  | ✅        | Nombre de la empresa cliente atendida (texto libre) |
| `category`           | string  | ✅        | Ver categorías abajo                                |
| `description`        | string  | ✅        | Texto libre, mínimo 5 caracteres                    |
| `agent_id`           | string  | ✅        | Formato `AGT-XX` (ej.: `AGT-07`)                    |
| `status`             | string  | ✅        | `OPEN`, `CLOSED`, `DISCARDED`                       |
| `customer_email`     | string  | ✅        | Email válido del cliente final (**sensible**)       |
| `satisfaction_score` | integer | ❌\*      | Entero 1–5. **Requerido si** `status = CLOSED`      |

\*`satisfaction_score` es opcional en la estructura, pero un registro `CLOSED` sin este valor se considera **incompleto**.

> ⚠️ El campo `customer_email` contiene correos reales y por eso este archivo no puede compartirse con herramientas de IA externas. Tu script nunca debe imprimir, registrar ni exportar direcciones de correo individuales en ninguna salida.

### Categorías válidas

| Código      | Descripción                                             |
| ----------- | ------------------------------------------------------- |
| `TECHNICAL` | Problema técnico con un producto o sistema              |
| `BILLING`   | Consulta o disputa de facturación                       |
| `ACCESS`    | Problema de acceso, login o permisos                    |
| `HR_QUERY`  | Consulta de RR. HH. o políticas de personal de clientes |
| `COMPLAINT` | Queja formal sobre la calidad del servicio              |

---

## Reglas de registros inválidos

Un registro debe marcarse como **inválido** si ocurre cualquiera de estos casos:

| Regla                                        | Descripción                                                  |
| -------------------------------------------- | ------------------------------------------------------------ |
| Falta `client_company`                       | El campo está vacío                                          |
| `category` faltante o inválida               | El campo está vacío o no está entre las 5 categorías válidas |
| `description` vacía                          | El campo está vacío o tiene menos de 5 caracteres            |
| `agent_id` faltante o inválido               | El campo está vacío o no cumple el formato `AGT-XX`          |
| `customer_email` faltante o inválido         | El campo está vacío o no contiene `@`                        |
| `status = CLOSED` y sin `satisfaction_score` | Ticket cerrado sin puntaje registrado                        |
| `satisfaction_score` fuera de rango          | Hay valor, pero no está entre 1 y 5 (inclusive)              |

Tu script debe reportar cuántos registros caen en cada tipo de regla.

---

## Distribución de datos (archivo de prueba provisto)

El archivo `incidents-nexova.csv` se envió como adjunto (ver ficheros `incidents-nexova.csv`). Los siguientes valores describen su contenido y son los que tu script debe producir exactamente.

**Total de filas:** 100

**Registros válidos: 96**
| Categoría | Cantidad |
|---|---|
| `TECHNICAL` | 28 |
| `BILLING` | 18 |
| `ACCESS` | 21 |
| `HR_QUERY` | 17 |
| `COMPLAINT` | 12 |

| Estado      | Cantidad |
| ----------- | -------- |
| `OPEN`      | 27       |
| `CLOSED`    | 56       |
| `DISCARDED` | 13       |

**Registros inválidos: 4**
| Regla activada | Cantidad |
|---|---|
| Falta `client_company` | 1 |
| `category` faltante o inválida | 1 |
| `customer_email` faltante o inválido | 1 |
| `status = CLOSED` sin `satisfaction_score` | 1 |

**Puntajes de satisfacción (56 registros cerrados)**
| Puntaje | Cantidad |
|---|---|
| 1 | 2 |
| 2 | 5 |
| 3 | 10 |
| 4 | 22 |
| 5 | 17 |
Promedio: **3.84**

---

## Salida esperada

Cuando el estudiante ejecute `python analyze.py incidents-nexova.csv` con el archivo provisto, la salida en consola debe mostrar los siguientes valores:

```
============================================================
  NEXOVA — SUPPORT TICKET ANALYSIS
  Source file: incidents-nexova.csv
============================================================

TOTAL RECORDS IN FILE .......... 100
  ├─ Valid records ................ 96
  └─ Invalid / incomplete .......... 4

INVALID RECORDS BREAKDOWN
  ├─ Missing client_company ........ 1
  ├─ Invalid or missing category ... 1
  ├─ Invalid or missing email ...... 1
  └─ Closed ticket, no score ....... 1

BREAKDOWN BY CATEGORY (valid records)
  ├─ TECHNICAL .................... 28  (29.2%)
  ├─ BILLING ...................... 18  (18.8%)
  ├─ ACCESS ....................... 21  (21.9%)
  ├─ HR_QUERY ..................... 17  (17.7%)
  └─ COMPLAINT .................... 12  (12.5%)

BREAKDOWN BY STATUS (valid records)
  ├─ OPEN ......................... 27  (28.1%)
  ├─ CLOSED ....................... 56  (58.3%)
  └─ DISCARDED .................... 13  (13.5%)

SATISFACTION INDEX (closed tickets)
  Scored tickets: 56 of 56
  Average score: 3.84 / 5.00
  ├─ Score 1 (Very dissatisfied) ... 2
  ├─ Score 2 (Dissatisfied) ........ 5
  ├─ Score 3 (Neutral) ............ 10
  ├─ Score 4 (Satisfied) .......... 22
  └─ Score 5 (Very satisfied) ..... 17

============================================================
Export results to CSV? [y / n]:
```

> **Nota:** Se aceptan diferencias menores de formato (espaciado, caracteres de caja), pero todos los valores numéricos deben coincidir exactamente.

---

## Nota de stakeholders

> **De Roberto Díaz (Customer Support Lead):**
> _"Necesitamos esto antes de la revisión con el cliente del viernes. La exportación CSV debe tener una métrica por fila; la voy a pegar en la plantilla del informe. Lo más importante: no incluyan ningún email de cliente en ninguna salida, ni siquiera en errores. Si un registro tiene email inválido, márcalo como 'invalid email', pero nunca imprimas la dirección."_

---

## Ruta en el repositorio

```
incidents-analysis/nexova-BRIEFING.md
```

---

_Documento interno — 4Geeks Academy · AI Engineering Track_  
_Para uso exclusivo en la generación de proyectos del programa_

---

# BRIEFING — Directorio de Proveedores · Nexova

_These instructions are also available in [English](./nexova-BRIEFING.en.md)._

> **Milestone:** 09 — Lightweight Storage API  
> **Ruta en el repositorio:** `09-lightweight-storage/nexova-BRIEFING.md`

---

## Tu empresa

Eres parte del equipo de AI Engineering de **Nexova**, una consultora de recursos humanos y adquisición de talento con sede en Valencia (España) y oficina en Miami (Florida). Tu tech lead es **Sergio Molina**, CTO, y el proyecto ha sido solicitado por **Patricia Solís**, HR Manager, en coordinación con el área de operaciones.

Nexova contrata servicios externos de forma recurrente: plataformas de publicación de ofertas de empleo, herramientas de selección, proveedores de formación, software corporativo y servicios de outsourcing. Hasta ahora, este registro vive en una hoja de cálculo que Patricia actualiza manualmente y comparte por email cada vez que hay un cambio. El resultado son múltiples versiones circulando en paralelo sin que nadie sepa cuál es la vigente. Este proyecto crea el registro oficial y único.

---

## Modelo de proveedor

Cada proveedor en el directorio de Nexova tiene la siguiente estructura:

| Campo                   | Tipo                                  | Descripción                                             |
| ----------------------- | ------------------------------------- | ------------------------------------------------------- |
| `name`                  | string, requerido                     | Nombre comercial del proveedor o plataforma             |
| `country`               | string, requerido                     | País del contrato activo: `"Spain"` o `"USA"`           |
| `categories`            | lista de strings, requerido, mínimo 1 | Tipo de servicio que provee (ver lista válida)          |
| `monthly_rate`          | float, requerido, > 0                 | Coste mensual vigente en la moneda del contrato         |
| `currency`              | string, requerido                     | `"EUR"` para Spain, `"USD"` para USA                    |
| `updated_at`            | datetime, generado por el sistema     | Timestamp de la última actualización de tarifa          |
| `status`                | string, requerido                     | `"active"` o `"suspended"`                              |
| `contract_renewal_date` | string, opcional                      | Fecha de renovación del contrato (formato `YYYY-MM-DD`) |
| `contact_email`         | string, opcional                      | Email del account manager del proveedor                 |
| `notes`                 | string, opcional                      | Observaciones internas                                  |

### Categorías válidas

```python
VALID_CATEGORIES = [
    "job_boards",
    "ats_software",
    "assessment_tools",
    "training_platforms",
    "payroll_and_hr_software",
    "video_interview",
    "background_check",
    "office_and_facilities",
    "it_and_software_licenses"
]
```

### Estados válidos

```python
VALID_STATUSES = ["active", "suspended"]
```

---

## Datos iniciales del seeder

El seeder debe cargar exactamente los siguientes proveedores, que representan el estado actual del directorio de Patricia.

```python
SUPPLIERS_SEED = [
    {
        "name": "LinkedIn Talent Solutions",
        "country": "Spain",
        "categories": ["job_boards"],
        "monthly_rate": 1200.0,
        "currency": "EUR",
        "status": "active",
        "contract_renewal_date": "2025-03-31",
        "contact_email": "account@linkedin.com",
        "notes": "Licencia corporativa para publicación de ofertas y búsqueda de candidatos."
    },
    {
        "name": "InfoJobs Premium",
        "country": "Spain",
        "categories": ["job_boards"],
        "monthly_rate": 490.0,
        "currency": "EUR",
        "status": "active",
        "contract_renewal_date": "2025-06-30",
        "contact_email": "empresas@infojobs.net"
    },
    {
        "name": "Indeed Sponsored",
        "country": "USA",
        "categories": ["job_boards"],
        "monthly_rate": 850.0,
        "currency": "USD",
        "status": "active",
        "contact_email": "sales@indeed.com",
        "notes": "Campañas de pago por clic para perfiles de customer support en Miami."
    },
    {
        "name": "Workable",
        "country": "Spain",
        "categories": ["ats_software"],
        "monthly_rate": 299.0,
        "currency": "EUR",
        "status": "active",
        "contract_renewal_date": "2025-09-15",
        "contact_email": "support@workable.com",
        "notes": "ATS principal para el equipo de selección de Valencia."
    },
    {
        "name": "Greenhouse",
        "country": "USA",
        "categories": ["ats_software"],
        "monthly_rate": 620.0,
        "currency": "USD",
        "status": "suspended",
        "contact_email": "accounts@greenhouse.io",
        "notes": "Suspendido tras no renovar. Sergio está evaluando si migrar todo a Workable."
    },
    {
        "name": "Thomas International",
        "country": "Spain",
        "categories": ["assessment_tools"],
        "monthly_rate": 380.0,
        "currency": "EUR",
        "status": "active",
        "contract_renewal_date": "2025-12-01",
        "contact_email": "clientes@thomas.es",
        "notes": "Tests de personalidad y aptitud para procesos de mandos intermedios."
    },
    {
        "name": "HireVue",
        "country": "USA",
        "categories": ["video_interview"],
        "monthly_rate": 540.0,
        "currency": "USD",
        "status": "active",
        "contract_renewal_date": "2025-08-31",
        "contact_email": "support@hirevue.com"
    },
    {
        "name": "Udemy Business",
        "country": "Spain",
        "categories": ["training_platforms"],
        "monthly_rate": 420.0,
        "currency": "EUR",
        "status": "active",
        "contract_renewal_date": "2026-01-15",
        "contact_email": "business@udemy.com",
        "notes": "Licencias para el equipo interno. Gestionado por Elena Vargas."
    },
    {
        "name": "Coursera for Teams",
        "country": "USA",
        "categories": ["training_platforms"],
        "monthly_rate": 399.0,
        "currency": "USD",
        "status": "suspended",
        "contact_email": "teams@coursera.com",
        "notes": "Suspendido por bajo uso. Revisar antes de Q4."
    },
    {
        "name": "Sage HR",
        "country": "Spain",
        "categories": ["payroll_and_hr_software"],
        "monthly_rate": 310.0,
        "currency": "EUR",
        "status": "active",
        "contract_renewal_date": "2025-10-01",
        "contact_email": "soporte@sage.com",
        "notes": "Software de nóminas y gestión de personal para la sede de Valencia."
    },
    {
        "name": "Gusto",
        "country": "USA",
        "categories": ["payroll_and_hr_software"],
        "monthly_rate": 280.0,
        "currency": "USD",
        "status": "active",
        "contact_email": "support@gusto.com",
        "notes": "Gestión de nóminas para los empleados de la oficina de Miami."
    },
    {
        "name": "Checkr",
        "country": "USA",
        "categories": ["background_check"],
        "monthly_rate": 195.0,
        "currency": "USD",
        "status": "active",
        "contract_renewal_date": "2025-11-30",
        "contact_email": "sales@checkr.com"
    },
    {
        "name": "Microsoft 365 Business",
        "country": "Spain",
        "categories": ["it_and_software_licenses"],
        "monthly_rate": 760.0,
        "currency": "EUR",
        "status": "active",
        "contact_email": "enterprise@microsoft.com",
        "notes": "Licencias para toda la plantilla de Valencia y Miami."
    },
    {
        "name": "Regus Valencia",
        "country": "Spain",
        "categories": ["office_and_facilities"],
        "monthly_rate": 2400.0,
        "currency": "EUR",
        "status": "active",
        "contract_renewal_date": "2025-07-01",
        "contact_email": "valencia@regus.com",
        "notes": "Alquiler de la oficina principal en Valencia. Incluye sala de reuniones."
    },
    {
        "name": "WeWork Miami",
        "country": "USA",
        "categories": ["office_and_facilities"],
        "monthly_rate": 3100.0,
        "currency": "USD",
        "status": "active",
        "contract_renewal_date": "2025-09-30",
        "contact_email": "miami@wework.com"
    }
]
```

---

## Restricciones de negocio

- **Moneda por país:** Un proveedor de `"Spain"` debe tener `currency = "EUR"`. Un proveedor de `"USA"` debe tener `currency = "USD"`. La API debe rechazar combinaciones inconsistentes.
- **Trazabilidad de tarifas:** Cada actualización de `monthly_rate` debe registrar el `updated_at` automáticamente. Patricia usa este dato para justificar variaciones de presupuesto ante dirección.
- **Renovaciones próximas:** El campo `contract_renewal_date` es opcional pero relevante — los proveedores con renovación en los próximos 60 días deben destacarse visualmente en el frontend.
- **Suspensión controlada:** Los proveedores suspendidos no se eliminan. Permanecen en el directorio con estado `"suspended"` para mantener el historial de relaciones comerciales.

---

## Lo que verá Patricia en el frontend

La página del directorio debe permitirle a Patricia:

1. Ver todos los proveedores agrupados o filtrables por país (Spain / USA).
2. Filtrar por categoría para responder preguntas como "¿qué herramientas de ATS tenemos activas?".
3. Distinguir de un vistazo los proveedores activos de los suspendidos.
4. Registrar un proveedor nuevo desde un formulario.
5. Actualizar la tarifa mensual de un proveedor y ver el cambio reflejado inmediatamente.
6. Activar o suspender un proveedor con un control visible en cada fila.

---

_Documento interno — 4Geeks Academy · AI Engineering Track_
