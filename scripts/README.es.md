# Carpeta `scripts`

## Carga histórica de incidencias

`seed_incidents.py` importa incidencias válidas desde `incidents-nexova.csv` hacia la tabla `incidents` de TinyDB. Valida el esquema legado con las funciones compartidas en `packages/shared/python/nexova_shared/incident_csv.py`, aplica los mapeos del briefing y omite duplicados usando el `ticket_id` como clave de importación. Los correos del CSV no se guardan ni se muestran en consola.

Requiere las dependencias Python del servicio API instaladas. Desde la raíz del repositorio:

```bash
python scripts/seed_incidents.py
python scripts/seed_incidents.py ruta/al/archivo.csv
python scripts/seed_incidents.py --db services/api/data/verification.json
```

Esta carpeta contiene **scripts auxiliares** del monorepo: automatizaciones de desarrollo, utilidades de mantenimiento, tareas repetitivas (setup, lint, migraciones, generación de datos, etc.) y tooling interno.

- **Propósito principal**: agrupar herramientas de soporte que no pertenecen a una app/agente/pipeline específico, pero facilitan el trabajo del equipo.
- **Recomendación**: documenta cada script (qué hace, parámetros, requisitos, ejemplos de uso) y procura que sean reproducibles (y seguros) en distintos entornos.
