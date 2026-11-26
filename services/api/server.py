"""Local HTTP API for Nexova incident analysis."""

import csv
import io
import json
import sys
import uuid
from email import policy
from email.parser import BytesParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock

from incident_analysis import CATEGORIES, ISSUES, STATUSES, analyze_stream, metrics


MAX_UPLOAD_BYTES = 10 * 1024 * 1024
latest_csv = None
latest_id = None
latest_lock = Lock()


def summarize(result):
    totals, issues, categories, statuses, scores = result
    scored = sum(scores.values())
    average = sum(score * count for score, count in scores.items()) / scored if scored else None
    return {
        "total": totals["total"],
        "valid": totals["valid"],
        "invalid": totals["invalid"],
        "issues": {key: {"label": label, "count": issues[key]} for key, label in ISSUES.items()},
        "categories": {category: categories[category] for category in CATEGORIES},
        "statuses": {status: statuses[status] for status in STATUSES},
        "satisfaction": {
            "scored": scored,
            "closed": statuses["CLOSED"],
            "average": float(f"{average:.2f}") if average is not None else None,
            "scores": {str(score): scores[score] for score in range(1, 6)},
        },
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def respond(self, status, body, content_type, headers=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def json_response(self, status, data):
        self.respond(status, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_POST(self):
        global latest_csv, latest_id
        if self.path != "/api/incidents/analyze":
            self.json_response(404, {"error": "Ruta no encontrada."})
            return
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self.json_response(411, {"error": "Se requiere una longitud de contenido valida."})
            return
        if length <= 0:
            self.json_response(400, {"error": "La solicitud esta vacia."})
            return
        if length > MAX_UPLOAD_BYTES:
            self.json_response(413, {"error": "El fichero supera el limite de 10 MB."})
            return
        content_type = self.headers.get("Content-Type", "")
        if not content_type.lower().startswith("multipart/form-data;"):
            self.json_response(415, {"error": "Se requiere multipart/form-data con un fichero CSV."})
            return
        body = self.rfile.read(length)
        message = BytesParser(policy=policy.default).parsebytes(
            b"Content-Type: " + content_type.encode("ascii", errors="replace") + b"\r\nMIME-Version: 1.0\r\n\r\n" + body
        )
        if message.defects or not message.is_multipart():
            self.json_response(400, {"error": "El formulario multipart tiene un formato incorrecto."})
            return
        files = [part for part in message.iter_parts() if part.get_param("name", header="content-disposition") == "file" and part.get_filename() is not None]
        if len(files) != 1:
            self.json_response(400, {"error": "Adjunta exactamente un fichero en el campo file."})
            return
        data = files[0].get_payload(decode=True)
        if not data or not data.strip():
            self.json_response(400, {"error": "El fichero CSV esta vacio."})
            return
        try:
            text = data.decode("utf-8-sig")
            result = analyze_stream(io.StringIO(text, newline=""))
        except UnicodeDecodeError:
            self.json_response(400, {"error": "El CSV debe estar codificado en UTF-8."})
            return
        except (csv.Error, ValueError):
            self.json_response(400, {"error": "El CSV tiene un formato o una cabecera incorrectos."})
            return
        if not result[0]["total"]:
            self.json_response(400, {"error": "El CSV no contiene registros."})
            return

        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(("metrica", "valor"))
        writer.writerows(metrics(result))
        analysis_id = uuid.uuid4().hex
        with latest_lock:
            latest_csv = output.getvalue().encode("utf-8")
            latest_id = analysis_id
        self.json_response(200, {**summarize(result), "analysis_id": analysis_id})

    def do_GET(self):
        if self.path != "/api/incidents/results/export":
            self.json_response(404, {"error": "Ruta no encontrada."})
            return
        with latest_lock:
            output = latest_csv
            analysis_id = latest_id
        if output is None:
            self.json_response(404, {"error": "Todavia no hay un analisis para exportar."})
            return
        if self.headers.get("If-Match") and self.headers.get("If-Match") != analysis_id:
            self.json_response(409, {"error": "Hay un analisis mas reciente. Vuelve a analizar el archivo antes de descargarlo."})
            return
        self.respond(200, output, "text/csv; charset=utf-8", {"Content-Disposition": 'attachment; filename="results.csv"'})


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"API de incidencias disponible en http://127.0.0.1:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()