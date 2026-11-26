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

## Análisis de incidencias

Requiere Python 3 y únicamente utiliza la biblioteca estándar. Desde la raíz del repositorio:

```bash
python scripts/analyze.py ruta/al/incidents-nexova.csv
```

El CSV debe tener la cabecera y los campos descritos en [el briefing de incidencias](../nexova-BRIEFING.es.md). El informe incluye registros válidos e inválidos, motivos de invalidez, categorías, estados y satisfacción de las incidencias cerradas. Una fila con varios problemas se cuenta una sola vez como inválida, pero una vez por cada motivo. También se comprueban los formatos y unicidad de identificadores, fechas, estados y el número de columnas.

Al responder `s`, se escribe `results.csv` en el directorio desde el que se ejecuta el comando, con una métrica por fila. Se reemplaza cualquier archivo existente con ese nombre, salvo si es el archivo de entrada. Los correos individuales no aparecen en los informes ni en los errores.

Para ejecutar las pruebas con datos ficticios:

```bash
python -m unittest discover -s scripts -p 'test_analyze.py' -v
```
