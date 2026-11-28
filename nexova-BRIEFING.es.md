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

---

# BRIEFING — Gestor de Incidencias Centralizado · Nexova

_Hito: integración de un gestor centralizado de incidencias en la plataforma interna._

## Empresa y objetivo

Nexova es una consultora de recursos humanos y adquisición de talento con 120 empleados, sede en Valencia y oficina en Miami. Sus líneas de negocio incluyen headhunting, outsourcing de equipos de soporte al cliente y formación corporativa. El gestor debe registrar incidencias técnicas y operativas, incluidas quejas de clientes, errores en selección y problemas del equipo de soporte externalizado.

## Usuarios y necesidades

- **Sergio Molina (CTO):** necesita una vista central de problemas técnicos y operativos que hoy llegan por email, Slack o comunicación verbal, para medir y mejorar los tiempos de resolución.
- **Roberto Díaz (Customer Support Lead):** coordina 30 agentes que atienden incidencias de clientes. El equipo usa un helpdesk legado y no tiene una base de conocimiento centralizada.
- **Laura Mendoza (CEO):** necesita saber cuántas incidencias críticas siguen abiertas, de qué oficina proceden y cuánto tiempo llevan sin resolverse.

## Oficinas

El campo `branch` acepta exactamente estos valores:

| Valor | Nombre para mostrar |
| --- | --- |
| `central` | Central — sede Valencia |
| `valencia_operations` | Valencia — Operaciones |
| `miami_office` | Miami Office |
| `remote` | Remoto (empleado sin sede fija) |

Usa `central` si la incidencia no corresponde a una oficina concreta, por ejemplo, reportes internos de dirección o quejas de clientes sin sede asociada. `central` representa la sede central de Valencia; no crees otro valor para headquarters. Mantén `remote` visible y diferenciado de `central` y `valencia_operations`.

## Categorías

El campo `category` acepta exactamente uno de estos valores:

| Valor | Descripción |
| --- | --- |
| `technical_failure` | Fallo de sistema o herramienta tecnológica, como ATS, HubSpot, Zendesk o infraestructura |
| `process_error` | Error en un proceso operativo: selección, incorporación, formación o facturación |
| `client_complaint` | Queja o reclamación de un cliente corporativo sobre el servicio |
| `candidate_issue` | Problema reportado por o relacionado con un candidato en selección |
| `staff_issue` | Incidencia interna de RR. HH.: ausencia, conflicto, accidente o baja |
| `sla_breach` | Incumplimiento del SLA comprometido con un cliente |
| `data_quality` | Error o inconsistencia en datos de candidatos, clientes o reportes |
| `other` | Incidencia que no encaja en las categorías anteriores |

## Estados y ciclo de vida

| Estado | Significado |
| --- | --- |
| `open` | Incidencia registrada, aún sin responsable asignado |
| `in_progress` | Asignada a un equipo o persona y en gestión activa |
| `resolved` | Resuelta y confirmada por quien la reportó o por el responsable |
| `discarded` | Registrada por error, duplicada o fuera de alcance |

Transiciones válidas: `open` → `in_progress`, `open` → `discarded`, `in_progress` → `resolved` y `in_progress` → `discarded`. `resolved` y `discarded` son estados finales.

## Orígenes

| Valor | Cuándo se usa |
| --- | --- |
| `customer` | Reportada por un cliente corporativo que contrata servicios de Nexova |
| `branch` | Reportada por personal de una oficina de Nexova |
| `internal` | Detectada internamente por tecnología, operaciones o dirección |

## Carga histórica desde CSV

El CSV `incidents-nexova.csv`, del proyecto `incidents-file-analyzer` y ubicado en `content/contexts/incidents-file-analysis/`, contiene incidencias del helpdesk de soporte al cliente. Todas corresponden a clientes corporativos (`origin: "customer"`). El esquema del analizador usa campos, estados y categorías distintos: no insertes sus filas directamente. Reutiliza su lógica de validación y aplica las transformaciones descritas aquí antes de insertar. Descarta y reporta en consola los registros que no pasen la validación o no se puedan mapear.

Para idempotencia, identifica registros con `ticket_id`; si falta, usa la combinación `title + created_at`.

### Mapeo de campos

| Campo CSV | Campo del modelo | Transformación |
| --- | --- | --- |
| `ticket_id` | — | Solo control de duplicados; no se almacena |
| `description` | `title` | Primeros 120 caracteres, recortados; descarta el registro si queda vacío |
| `description` | `description` | Copia literal |
| `date` | `created_at` | Parsea `YYYY-MM-DD` como medianoche UTC; `updated_at` recibe el mismo instante al insertar |
| — | `origin` | Siempre `customer` para estos registros |
| — | `branch` | Siempre `central`, porque el CSV no contiene una oficina |

### Mapeo de estados y categorías

| CSV `status` | Modelo `status` |
| --- | --- |
| `OPEN` | `open` |
| `CLOSED` | `resolved` |
| `DISCARDED` | `discarded` |

| CSV `category` | Modelo `category` |
| --- | --- |
| `TECHNICAL` | `technical_failure` |
| `BILLING` | `process_error` |
| `ACCESS` | `technical_failure` |
| `HR_QUERY` | `process_error` |
| `COMPLAINT` | `client_complaint` |

## Conteos esperados tras la carga

Después de cargar el CSV, `/api/incidents/summary` debe devolver los conteos del modelo correspondientes a los 96 registros válidos (se excluyen las filas inválidas del CSV original).

| Estado del modelo | Conteo |
| --- | ---: |
| `open` | 27 |
| `resolved` | 56 |
| `discarded` | 13 |

| Categoría del modelo | Conteo |
| --- | ---: |
| `technical_failure` | 49 |
| `process_error` | 35 |
| `client_complaint` | 12 |

Estos son conteos post-transformación; el CSV de origen utiliza estados como `OPEN`/`CLOSED`/`DISCARDED` y categorías como `TECHNICAL`/`BILLING`.

## Notas de implementación

- Nexova opera en español en Valencia e inglés en Miami. Si los hitos previos incluyen soporte bilingüe, respétalo en el formulario y los mensajes de error.
- `sla_breach` es una categoría crítica para Roberto y Laura; diseña el modelo para que añadir un filtro por ella sea sencillo. Las alertas automáticas quedan fuera de este proyecto.

_Documento interno — 4Geeks Academy · AI Engineering Track_

---

# BRIEFING — Hito 5: Gestión de Inventario Backend con ORM y Doble Base de Datos
## Empresa: Nexova

**Ruta del briefing complementario:** `05-backend-inventory-orm/nexova-BRIEFING.es.md`.

> **Contexto de proyecto:** Este hito extiende el servicio FastAPI y la autenticación ya existentes en el monorepo. No se debe iniciar un repositorio nuevo ni rehacer esos componentes.
>
> **Ticket NXV-0201 — Sergio Molina (CTO):** Nexova necesita una API de inventario de equipos y materiales.
>
> “Una ‘entrada de activos’ es una compra o entrega recibida por la empresa. Una ‘salida de activos’ es una asignación a un empleado o un evento de consumo. El stock siempre es el resultado neto de entradas menos salidas — no se puede establecer directamente. Todas las rutas bajo `/inventory`. Consultad la especificación de entidades. Usad el UUID del usuario de TinyDB en cada orden.”

## Empresa y problema

Nexova cuenta con unos 120 empleados entre Valencia y Miami, seis oficinas, 30 agentes de soporte externalizados y ciclos de contratación constantes. Sus tres líneas de negocio —headhunting ejecutivo, atención al cliente externalizada y formación corporativa— dependen de que los equipos tecnológicos estén correctamente asignados. Sin embargo, IT y Operaciones carecen de visibilidad fiable sobre el hardware y los materiales disponibles, sus asignaciones y consumos: se extravían portátiles, se duplican asignaciones y los materiales de oficina se agotan sin aviso.

El sistema mantendrá la autenticación y los usuarios en TinyDB, y almacenará productos y órdenes de inventario en Supabase (PostgreSQL). FastAPI deberá mantener activas ambas conexiones y utilizar cada una para los datos que le corresponden. No se deben replicar usuarios en Supabase.

## Arquitectura y límites

- Usa SQLModel como ORM, que combina SQLAlchemy con los tipos de Pydantic. No uses SQLAlchemy directamente.
- Mantén las rutas de inventario en un `APIRouter` con prefijo `/inventory` y regístralo en la aplicación existente.
- Los modelos ORM y los schemas Pydantic de request/response deben estar en archivos separados.
- Ningún endpoint debe devolver directamente un objeto ORM.
- Las claves foráneas entre activos y órdenes deben aplicarse en PostgreSQL.
- La autenticación existente sigue usando TinyDB; `user_uuid` en cada orden referencia el UUID de ese sistema.

## Entidades y campos

Usa estos nombres exactamente en modelos, schemas y respuestas.

### `Asset` (equivale a `Product` en documentación previa)

| Campo | Tipo | Reglas |
| --- | --- | --- |
| `id` | `int` | Clave primaria autoincremental. |
| `name` | `str` | Nombre del activo, por ejemplo, `Portátil 14" Business`, `Ratón ergonómico` o `Resma de papel A4`. |
| `sku` | `str` | Código único, por ejemplo, `NXV-IT-001` o `NXV-OFF-003`. |
| `category` | `str` | `hardware`, `peripherals`, `office_supplies` o `training_materials`. |
| `office` | `str` | `Valencia` o `Miami`. |
| `current_stock` | `int` | Calculado desde las órdenes; no se almacena. Solo aparece en el schema de respuesta. |

### `AssetEntry` (equivale a `InboundOrder` en documentación previa)

Representa una compra o entrega de proveedor recibida por Nexova.

| Campo | Tipo | Reglas |
| --- | --- | --- |
| `id` | `int` | Clave primaria autoincremental. |
| `asset_id` | `int` | Clave foránea a `Asset`. |
| `quantity` | `int` | Unidades recibidas. |
| `supplier` | `str` | Nombre del proveedor o vendedor. |
| `office` | `str` | `Valencia` o `Miami`; oficina receptora. |
| `created_at` | `datetime` | Se establece automáticamente al crear la orden. |
| `user_uuid` | `str` | UUID del usuario de TinyDB responsable de registrar la entrada. |

### `AssetExit` (equivale a `OutboundOrder` en documentación previa)

Representa la asignación de un activo a un empleado o un evento de consumo.

| Campo | Tipo | Reglas |
| --- | --- | --- |
| `id` | `int` | Clave primaria autoincremental. |
| `asset_id` | `int` | Clave foránea a `Asset`. |
| `quantity` | `int` | Unidades asignadas o consumidas. |
| `exit_type` | `str` | `allocation` (asignación) o `consumption` (consumo). |
| `assigned_to` | `str \| None` | Nombre o ID del empleado para `allocation`; nulo para `consumption`. |
| `office` | `str` | `Valencia` o `Miami`. |
| `created_at` | `datetime` | Se establece automáticamente al crear la orden. |
| `user_uuid` | `str` | UUID del usuario de TinyDB responsable de registrar la salida. |

## API de inventario

Todos los endpoints están bajo `/inventory` y se implementan en `services/routers/inventory.py`.

| Método | Ruta | Comportamiento |
| --- | --- | --- |
| `GET` | `/inventory/products` | Lista todos los activos e incluye `current_stock` calculado. |
| `POST` | `/inventory/products` | Registra un activo nuevo. |
| `GET` | `/inventory/products/{id}` | Devuelve un activo y su stock actual. |
| `POST` | `/inventory/orders/inbound` | Registra una entrada `AssetEntry`. |
| `POST` | `/inventory/orders/outbound` | Registra una salida `AssetExit`. |
| `GET` | `/inventory/orders` | Lista entradas y salidas con los datos del activo. |

## Reglas de negocio y validación

1. Para cada activo, `current_stock = SUM(AssetEntry.quantity) - SUM(AssetExit.quantity)`. Se calcula al consultar y nunca se persiste como columna editable.
2. Rechaza una salida que supere el stock disponible antes de escribir en la base de datos. Responde `HTTP 400` con el mensaje exacto: `Insufficient stock for asset '{name}'. Available: {available}, requested: {quantity}.`.
3. `assigned_to` es obligatorio cuando `exit_type = "allocation"` y debe ser nulo cuando `exit_type = "consumption"`. Valídalo en el schema o en la lógica de ruta.
4. No crees una tabla o modelo de usuarios en SQLModel/Supabase. Los `user_uuid` hacen referencia a usuarios guardados en TinyDB.
5. Las oficinas `Valencia` y `Miami` coexisten en las mismas tablas; usa `office` para filtrar cuando corresponda.
6. El campo `office` debe estar tanto en los modelos como en los schemas de respuesta.

## Datos semilla de desarrollo

Crea al menos estos seis activos:

| name | sku | category | office |
| --- | --- | --- | --- |
| Portátil 14" Business | `NXV-IT-001` | `hardware` | Valencia |
| Portátil 14" Business | `NXV-IT-002` | `hardware` | Miami |
| Ratón ergonómico | `NXV-PER-001` | `peripherals` | Valencia |
| Hub USB-C | `NXV-PER-002` | `peripherals` | Miami |
| Resma de papel A4 | `NXV-OFF-001` | `office_supplies` | Valencia |
| Cuaderno de formación en liderazgo | `NXV-TRN-001` | `training_materials` | Valencia |

Registra al menos cuatro entradas: dos para `NXV-IT-001` (por ejemplo, 10 y 5 unidades) y una para cada uno de otros dos activos. Usa proveedores como `TechDistrib Valencia S.L.` y `Office Depot Miami`.

Registra al menos tres salidas. Incluye una `allocation` con `assigned_to` y una `consumption` con `assigned_to` nulo. Las salidas no pueden superar las entradas sembradas.

## Estructura indicada para `services/`

```text
services/
├── main.py
├── database.py          # TinyDB, motor SQLModel y dependencia get_db
├── models.py            # Asset, AssetEntry y AssetExit (SQLModel)
├── schemas.py           # Schemas Pydantic de request/response
└── routers/
    └── inventory.py     # APIRouter(prefix="/inventory")
```

La estructura describe la organización del servicio; debe adaptarse al monorepo existente sin duplicar ni reemplazar los componentes ya implementados.

## Criterios de aceptación

- Los endpoints funcionales de inventario responden bajo `/inventory`.
- Las relaciones y claves foráneas se aplican a nivel de base de datos.
- TinyDB y Supabase permanecen conectadas y cada tipo de dato se guarda en su almacén correspondiente.
- Una salida superior al stock recibe `HTTP 400` con el mensaje especificado y no crea una orden.
- Una asignación sin `assigned_to` se rechaza por validación; un consumo exige `assigned_to` nulo.
- `GET /inventory/products` refleja el stock neto de los datos sembrados.
- `office` está presente en modelos y schemas de respuesta.

---

_Documento interno — 4Geeks Academy · Track de Ingeniería de IA · Hito 5_
