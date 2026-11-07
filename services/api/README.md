# API de análisis de incidencias

Desde la raíz del repositorio, inicia la API con Python 3:

```bash
python services/api/server.py 8000
```

La API escucha en `127.0.0.1:8000`. `POST /api/incidents/analyze` recibe un CSV UTF-8 en el campo multipart `file` y devuelve el resumen JSON. `GET /api/incidents/results/export` descarga el último análisis como `results.csv`. El tamaño máximo de la solicitud es 10 MiB. Los CSV vacíos, sin registros o mal formados reciben una respuesta de error; los registros que incumplen las reglas del briefing se contabilizan como inválidos.

El JSON incluye `analysis_id`. Si se envía en la cabecera `If-Match` de la descarga, la API responde `409` cuando otro análisis ha sustituido al mostrado. Sin esa cabecera, devuelve el último análisis disponible. El estado es global al proceso y se pierde al reiniciar; una instancia nueva no tiene resultados para exportar. No se almacenan los registros individuales ni se registran o devuelven correos.

Este servidor es para uso interno local: no incluye autenticación, autorización, TLS ni persistencia compartida. No debe exponerse directamente a Internet ni utilizarse como servicio de producción sin implementar esas protecciones. Protege también el acceso al backoffice y su proxy.