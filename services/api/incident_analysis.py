"""Shared, privacy-preserving analysis of Nexova support tickets."""

import csv
import re
from collections import Counter
from datetime import date


CATEGORIES = ("TECHNICAL", "BILLING", "ACCESS", "HR_QUERY", "COMPLAINT")
STATUSES = ("OPEN", "CLOSED", "DISCARDED")
FIELDS = (
    "ticket_id", "date", "client_company", "category", "description",
    "agent_id", "status", "customer_email", "satisfaction_score",
)
ISSUES = {
    "ticket_id": "Identificador ausente, invalido o duplicado",
    "date": "Fecha ausente o invalida",
    "client_company": "Empresa cliente ausente",
    "category": "Categoria ausente o invalida",
    "description": "Descripcion ausente o demasiado corta",
    "agent_id": "Agente ausente o invalido",
    "status": "Estado ausente o invalido",
    "customer_email": "Email ausente o invalido",
    "missing_score": "Incidencia cerrada sin puntuacion",
    "invalid_score": "Puntuacion no entera o fuera de rango",
    "columns": "Numero de columnas incorrecto",
}


def validate(row, seen_ids):
    issues = set()
    ticket_id = row["ticket_id"]
    if not re.fullmatch(r"NXV-[0-9]{6}", ticket_id) or ticket_id in seen_ids:
        issues.add("ticket_id")
    if ticket_id:
        seen_ids.add(ticket_id)

    try:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", row["date"]):
            raise ValueError
        date.fromisoformat(row["date"])
    except ValueError:
        issues.add("date")

    if not row["client_company"]:
        issues.add("client_company")
    if row["category"] not in CATEGORIES:
        issues.add("category")
    if len(row["description"]) < 5:
        issues.add("description")
    if not re.fullmatch(r"AGT-[0-9]{2}", row["agent_id"]):
        issues.add("agent_id")
    if row["status"] not in STATUSES:
        issues.add("status")
    if "@" not in row["customer_email"]:
        issues.add("customer_email")

    score = row["satisfaction_score"]
    if not score and row["status"] == "CLOSED":
        issues.add("missing_score")
    elif score and not re.fullmatch(r"[1-5]", score):
        issues.add("invalid_score")
    return issues


def analyze_stream(source):
    totals = Counter()
    issues = Counter()
    categories = Counter()
    statuses = Counter()
    scores = Counter()
    seen_ids = set()

    reader = csv.reader(source, strict=True)
    header = next(reader, None)
    if header is None or len(header) != len(set(header)) or not set(FIELDS).issubset(header):
        raise ValueError("El CSV debe contener todas las columnas requeridas sin duplicados.")
    for values in reader:
        totals["total"] += 1
        if len(values) != len(header):
            totals["invalid"] += 1
            issues["columns"] += 1
            continue
        row = {field: value.strip() for field, value in zip(header, values)}
        row_issues = validate(row, seen_ids)
        if row_issues:
            totals["invalid"] += 1
            issues.update(row_issues)
            continue
        totals["valid"] += 1
        categories[row["category"]] += 1
        statuses[row["status"]] += 1
        if row["status"] == "CLOSED" and row["satisfaction_score"]:
            scores[int(row["satisfaction_score"])] += 1

    return totals, issues, categories, statuses, scores


def analyze(path):
    with path.open(encoding="utf-8-sig", newline="") as source:
        return analyze_stream(source)


def metrics(result):
    totals, issues, categories, statuses, scores = result
    scored = sum(scores.values())
    average = sum(score * count for score, count in scores.items()) / scored if scored else None
    rows = [
        ("Total de registros", totals["total"]),
        ("Registros validos", totals["valid"]),
        ("Registros invalidos", totals["invalid"]),
    ]
    rows.extend((f"Error: {label}", issues[key]) for key, label in ISSUES.items())
    rows.extend((f"Categoria: {category}", categories[category]) for category in CATEGORIES)
    rows.extend((f"Estado: {status}", statuses[status]) for status in STATUSES)
    rows.extend([
        ("Incidencias cerradas con puntuacion", scored),
        ("Satisfaccion media", f"{average:.2f}" if average is not None else "Sin datos"),
    ])
    rows.extend((f"Puntuacion: {score}", scores[score]) for score in range(1, 6))
    return rows