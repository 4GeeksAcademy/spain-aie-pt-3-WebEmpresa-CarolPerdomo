# Carpeta `packages`

Esta carpeta contiene **paquetes compartidos** del monorepo: librerías internas, utilidades, tipos, componentes comunes, SDKs, clientes y cualquier código reutilizable por varias aplicaciones/agentes/pipelines.

Cada subcarpeta dentro de `packages/` debería representar **un paquete versionable** (por ejemplo `shared-types`, `ui`, `analytics-sdk`) con su README propio.

- **Propósito principal**: fomentar reutilización y consistencia entre todos los desarrollos de la compañía.
- **Recomendación**: documenta los paquetes que vayas añadiendo, su API pública y cómo se consumen desde `apps/`, `agents/` y `workflows/`.

## Implementación de este proyecto

`shared/` contiene los tipos TypeScript del monorepo y la lógica Python compartida del gestor de incidencias. La validación y el mapeo CSV viven en [`shared/python/nexova_shared/incident_csv.py`](./shared/python/nexova_shared/incident_csv.py); los reutilizan `scripts/seed_incidents.py` y `services/api` para aplicar las mismas reglas antes de importar o guardar incidencias. Consulta [`shared/README.es.md`](./shared/README.es.md) para sus detalles.
