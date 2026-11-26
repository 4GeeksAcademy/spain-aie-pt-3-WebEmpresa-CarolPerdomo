# Paquete compartido

Este paquete reúne recursos utilizados por más de una parte del monorepo:

- `types/index.ts` y `package.json`: metadata y tipos TypeScript compartidos.
- `python/nexova_shared/incident_csv.py`: validación de campos del modelo de incidencia, validación de filas CSV, transformación de categorías/estados y creación de claves de importación.

La API (`services/api/nexova_suppliers/routes/incidents.py`) y el script histórico (`scripts/seed_incidents.py`) importan las mismas funciones Python. `services/api/nexova_suppliers/__init__.py` añade el paquete compartido a la ruta de importación de la API. Así evitan mantener reglas de validación duplicadas.

El script añade `packages/shared/python` a `sys.path` para poder ejecutarse desde la raíz del repositorio. Ejecuta los comandos de la API desde `services/api/` según el README de esa aplicación.
