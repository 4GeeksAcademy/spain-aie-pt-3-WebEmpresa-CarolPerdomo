# Propuesta de arquitectura backend para Nexova

**Estado:** propuesta; el repositorio todavía no contiene una API backend.

## Contexto y decisión

Nexova es una consultora de recursos humanos y adquisición de talento fundada en 2011, con unos 120 empleados y oficinas en Valencia y Miami. Su negocio abarca selección ejecutiva y de mandos medios, equipos externalizados de atención al cliente y formación corporativa. Hoy hay herramientas desconectadas y los CV pueden llegar por correo sin estructura; el sitio público y las aplicaciones internas del monorepo aún no comparten una API ni persistencia centralizada. El tracker de talento existe como frontend, pero sus métricas de backoffice son datos de referencia, no datos conectados a un servicio.

Se propone un **monolito modular, organizado por dominios y con capas internas**. Es una API desplegable como una unidad, pero sus módulos separan reglas de negocio, casos de uso, transporte HTTP y persistencia. No se recomienda empezar con microservicios: el equipo y las necesidades descritas no justifican todavía la complejidad de despliegues, observabilidad, seguridad y comunicación distribuida. Tampoco se propone MVC clásico como estructura principal: FastAPI sirve una API y no necesita una vista de servidor que renderice las interfaces; los frontends son aplicaciones separadas.

La separación por dominios representa el trabajo real de Nexova, no solo el tipo técnico de cada archivo. Las capas dentro de cada dominio mantienen los routers HTTP delgados y evitan que las reglas de selección, por ejemplo, queden acopladas a FastAPI o a una base de datos concreta. Es una aplicación pragmática de arquitectura en capas y puertos/adaptadores, sin exigir una implementación de DDD completa.

### Por qué encaja

- **Talento es el primer límite de negocio útil.** El registro de profesionales y el trabajo de selección necesitan compartir candidatos, estados, etapas y notas, con acceso controlado para el equipo de reclutamiento.
- **Las otras líneas tienen reglas distintas.** La gestión de clientes, la operación de equipos de atención y la formación pueden crecer sin mezclar sus conceptos con el expediente de candidatos.
- **El tamaño favorece una operación sencilla.** Un solo servicio mantiene un despliegue y una configuración operables por el equipo actual, mientras los límites entre módulos conservan una ruta de evolución.
- **El monorepo ya contempla servicios transversales.** `services/` es el lugar documentado para APIs y workers; los frontends viven como aplicaciones con sus propios paquetes.
- **Permite extraer componentes más adelante con evidencia.** Un módulo podría separarse si adquiere necesidades independientes de escala, disponibilidad, seguridad, propiedad de equipo o cadencia de despliegue; no se presupone que eso vaya a ocurrir.

## Organización propuesta

El backend se añadiría como un servicio independiente dentro del monorepo. Esta estructura es un punto de partida: se crean los dominios que requiera el primer alcance y los demás se incorporan cuando exista un caso de uso respaldado por el negocio.

```text
services/
  nexova-api/
    pyproject.toml
    README.md
    .env.example
    alembic.ini
    migrations/
    app/
      main.py
      api/
        v1/
          router.py
      core/
        config.py
        security.py
        logging.py
        errors.py
      db/
        session.py
        base.py
      domains/
        talent/
          router.py
          schemas.py
          service.py
          entities.py
          models.py
          repository.py
          policies.py
        clients/
          router.py
          schemas.py
          service.py
          entities.py
          models.py
          repository.py
        workforce/
          router.py
          schemas.py
          service.py
          entities.py
          models.py
          repository.py
        learning/
          router.py
          schemas.py
          service.py
          entities.py
          models.py
          repository.py
      infrastructure/
        integrations/
        persistence/
    tests/
      api/
      domains/
      integration/
```

### Criterio de separación

- **`api/v1/`** ensambla los routers públicos de la versión HTTP. No contiene reglas de negocio.
- **`core/`** contiene configuración transversal, autenticación/autorización, logging y manejo común de errores. No debe convertirse en un almacén de funcionalidades de negocio.
- **`db/` y `migrations/`** centralizan la sesión/conexión y los cambios versionados del esquema. Las migraciones se revisan como cambios de contrato y datos.
- **`domains/talent/`** contiene el alta de profesionales y el pipeline interno de selección: perfiles, estado/etapa, notas y sus reglas de acceso. Es el dominio inicial más próximo a la necesidad de estructurar candidaturas.
- **`domains/clients/`** separa cuentas de empresas y solicitudes comerciales de la captación de candidatos. Los contactos de empresas nunca se modelan como candidatos.
- **`domains/workforce/`** representa equipos y asignaciones de los servicios externalizados de atención al cliente.
- **`domains/learning/`** representa programas y sesiones de formación corporativa.
- **`router.py`** declara las operaciones HTTP del dominio y traduce entre HTTP y los casos de uso; **`schemas.py`** define contratos de entrada/salida de Pydantic; **`service.py`** implementa casos de uso; **`entities.py`** expresa conceptos/reglas del dominio; **`models.py`** representa persistencia; y **`repository.py`** abstrae el acceso a datos. Las rutas no consultan directamente la base de datos.
- **`infrastructure/`** aloja adaptadores concretos para persistencia e integraciones externas, como correo o CRM, si se aprueban y construyen. No se asume que esas integraciones existan.
- **`shared/` no se crea de inicio.** Solo se añade si hay conceptos realmente neutrales reutilizados por más de un dominio; las reglas de talento no deben acabar como utilidades globales.
- **`tests/`** refleja los límites: pruebas unitarias de reglas y casos de uso, pruebas HTTP de routers y pruebas de integración para persistencia e integraciones.

Para el primer incremento, se implementarían solo las partes necesarias de `talent` y, si el formulario de empresas requiere captura backend, una operación pública de consultas comerciales. `clients`, `workforce` y `learning` son límites previstos, no módulos existentes ni una promesa de construirlos ahora.

## Routers y endpoints FastAPI

Cada dominio expone un `APIRouter`; el router central de `api/v1/router.py` los incorpora con prefijos, etiquetas y dependencias comunes. Así, `main.py` crea la aplicación y conecta configuración y middleware sin convertirse en un catálogo de endpoints. Los contratos usan recursos y operaciones HTTP; la versión va en el prefijo `/api/v1` para que una evolución incompatible pueda publicarse de forma controlada.

| Grupo | Rutas propuestas | Propósito y acceso |
| --- | --- | --- |
| Salud | `GET /health/live`, `GET /health/ready` | Comprobar proceso y disponibilidad para despliegue; no exponen datos de negocio. |
| Captación pública | `POST /api/v1/public/talent-registrations` | Recibir el formulario de profesionales, validar de nuevo en el servidor y registrar el consentimiento. No devuelve datos de otros candidatos. |
| Contacto comercial público | `POST /api/v1/public/service-inquiries` | Capturar consultas de empresas, separadas del banco de talento. Se implementa cuando se defina ese flujo. |
| Pipeline de talento | `GET /api/v1/talent/candidates`, `POST /api/v1/talent/candidates`, `GET /api/v1/talent/candidates/{candidate_id}`, `PATCH /api/v1/talent/candidates/{candidate_id}` | Listado con paginación, búsqueda y filtros de estado/etapa; alta manual; detalle y actualización de perfil o estado. Solo personal autorizado. |
| Notas de selección | `POST /api/v1/talent/candidates/{candidate_id}/notes`, `DELETE /api/v1/talent/candidates/{candidate_id}/notes/{note_id}` | Añadir y retirar notas internas asociadas a una candidatura. Requiere autorización y registro de auditoría apropiado. |
| Clientes | `/api/v1/clients` y `/api/v1/clients/{client_id}` | Consultar/gestionar cuentas de empresas y su relación comercial; separado del perfil profesional. |
| Equipos externalizados | `/api/v1/workforce/teams` y `/api/v1/workforce/assignments` | Gestionar equipos de atención y asignaciones cuando ese proceso entre en alcance. |
| Formación | `/api/v1/learning/programs` y `/api/v1/learning/sessions` | Consultar/gestionar programas y sesiones corporativas si se incorpora esa capacidad. |

Los grupos de `clients`, `workforce` y `learning` son ejemplos de contratos futuros, no una especificación exhaustiva. Sus métodos y permisos se concretarían junto con los procesos responsables antes de implementarlos. El API documentaría filtros, paginación y errores; no incluiría emails ni otros datos personales en rutas o parámetros de búsqueda registrados en logs. FastAPI puede publicar el esquema OpenAPI para que los clientes frontend conozcan los contratos sin acceder a la base de datos.

## Convenciones de FastAPI que guían la propuesta

La guía oficial de FastAPI para aplicaciones grandes muestra una aplicación dividida en paquetes/módulos, con `APIRouter` por área y composición desde la aplicación principal mediante `include_router`. De ahí se toma la separación de routers y el montaje centralizado; en Nexova, el criterio para esas áreas es el dominio de negocio y no una única carpeta global de rutas para cada recurso técnico.

FastAPI permite declarar dependencias compartidas para autenticación, permisos y recursos como sesiones de base de datos. Se propone resolverlas en los routers o casos de uso según el límite que protejan y mantenerlas fuera de lógica repetida en cada endpoint. Los modelos de Pydantic que forman el contrato HTTP se mantienen separados de los modelos de persistencia para evitar que un cambio interno de base de datos cambie accidentalmente la API.

La documentación de configuración de FastAPI recomienda settings a partir de variables de entorno, con validación tipada (por ejemplo, `pydantic-settings`). Por eso `core/config.py` centraliza y valida configuración; los valores locales pueden venir de un `.env` ignorado por Git, mientras `.env.example` enumera nombres y ejemplos no secretos. La guía de CORS confirma que un origen incluye protocolo, host y puerto, y que los navegadores restringen llamadas entre orígenes distintos: la política debe configurarse explícitamente para las interfaces autorizadas.

## Frontend y backend como sistemas separados

### Repositorio y despliegue

Se recomienda **mantenerlos en este monorepo por ahora**: ya agrupa las aplicaciones de web pública, backoffice y tracker de talento, y documenta `services/` como destino para APIs. Esto facilita revisar cambios coordinados de contrato y frontend y mantiene un contexto común. Cada aplicación conserva su paquete, dependencias, instrucciones y proceso de despliegue; el monorepo no implica que todas se publiquen juntas. CI y despliegues deben poder limitarse al servicio o aplicación afectada.

La separación en repositorios sería razonable si aparecen equipos con permisos y propiedad independientes, ciclos de publicación incompatibles o requisitos de aislamiento que compensen el coste de coordinar contratos y versiones. No se propone dividir ahora sin esa evidencia.

### Comunicación y configuración

- Las interfaces consumen la API por HTTPS y por los contratos JSON documentados en OpenAPI; no comparten la base de datos ni importan modelos ORM del backend. Los cambios incompatibles requieren una versión de API o una migración coordinada y documentada.
- La URL base de la API se configura por entorno. En los frontends Next.js, una variable con prefijo `NEXT_PUBLIC_` se considera visible para el navegador: solo debe contener información pública, como una URL de API. Credenciales de base de datos, claves privadas y secretos permanecen del lado servidor y se inyectan en el entorno de despliegue.
- El backend recibe configuración propia (por ejemplo, URL de base de datos, orígenes permitidos y claves de integración) desde el entorno/gestor de secretos. No se suben archivos `.env` reales; `.env.example` no contiene credenciales válidas.
- CORS se configura en el backend con una lista explícita de orígenes de desarrollo y producción que corresponden a las aplicaciones autorizadas, incluidos sus puertos locales. Se permiten solo métodos y cabeceras necesarios. Si se usan cookies/credenciales, se configuran expresamente origen y credenciales; no se combina un origen comodín con credenciales.
- CORS es una política del navegador, no autenticación ni control de acceso. Los endpoints internos siguen exigiendo identidad y autorización en el servidor, y todo el tráfico de producción usa TLS.

## Riesgos y puntos de atención

| Riesgo | Qué puede salir mal | Prevención propuesta |
| --- | --- | --- |
| Endpoints con lógica de negocio y acceso a datos | Los routers crecen, las reglas se duplican y resulta difícil probar cambios sin levantar toda la API. | Mantener routers como adaptadores HTTP; llevar casos de uso y reglas a servicios/dominio y probarlos por separado. |
| Cruce entre dominios o `shared/` sin límites | Clientes, candidatos y empleados se confunden; aparecen importaciones circulares y cambios locales rompen áreas ajenas. | Asignar un propietario de datos por dominio, exponer operaciones mediante casos de uso y mover a `shared` únicamente conceptos neutrales. |
| CORS amplio o confundir CORS con seguridad | Un origen no autorizado puede leer respuestas en el navegador; aun con CORS estricto, endpoints sin permisos siguen expuestos. | Lista por entorno de orígenes exactos, revisión de credenciales, autenticación/autorización del lado servidor y pruebas de configuración. |
| Manejo débil de datos de candidatos | CVs, contacto, consentimiento o notas internas pueden filtrarse en logs, exponerse a roles indebidos o conservarse sin política clara. | Minimizar y proteger datos, limitar permisos por función, redactar logs, auditar accesos/cambios y definir retención, borrado y atención de derechos con asesoría de privacidad aplicable a España/UE y EE. UU. |
| Contrato API cambia sin coordinación | La web, el backoffice o el tracker dejan de funcionar al publicarse una modificación incompatible. | Revisar cambios OpenAPI, mantener compatibilidad aditiva cuando sea posible, versionar cambios incompatibles y validar consumidores antes del despliegue. |

## Referencias consultadas

- [FastAPI: Bigger Applications - Multiple Files](https://fastapi.tiangolo.com/tutorial/bigger-applications/): organización por paquetes, `APIRouter` y montaje con `include_router`.
- [FastAPI: Settings and Environment Variables](https://fastapi.tiangolo.com/advanced/settings/): configuración tipada desde variables de entorno y uso de settings.
- [FastAPI: CORS](https://fastapi.tiangolo.com/tutorial/cors/): definición de origen, comunicación navegador/API, lista de orígenes y consideraciones sobre comodines y credenciales.
- [FastAPI: Response Model](https://fastapi.tiangolo.com/tutorial/response-model/): validación y documentación de los datos que devuelve una operación.
- [MDN: Cross-Origin Resource Sharing (CORS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS): referencia del mecanismo CORS del navegador y solicitudes preflight.

Estas referencias sustentan las convenciones del framework; la elección de monolito modular y los límites propuestos se derivan de la estructura del repositorio y de las necesidades conocidas de Nexova. La propuesta no afirma que FastAPI, una base de datos, autenticación ni integraciones estén instalados o implementados.
