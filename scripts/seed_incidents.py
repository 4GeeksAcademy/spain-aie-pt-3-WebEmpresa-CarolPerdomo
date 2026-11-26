"""Idempotently import validated incidents from the legacy support CSV.

Run from any working directory with the API dependencies installed:
    python scripts/seed_incidents.py [path/to/incidents-nexova.csv]

Customer email values are used only by the shared validator and are never
copied to the incident database or printed to the console.
"""

import csv
import argparse
import sys
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "services" / "api"))
sys.path.insert(0, str(REPO_ROOT / "packages" / "shared" / "python"))

from nexova_suppliers.database import SuppliersDB
from nexova_suppliers.models import IncidentCreate
from nexova_shared.incident_csv import (
    map_incident_row,
    source_key,
    validate_incident_csv_row,
    validate_incident_fields,
)


ISSUE_LABELS = {
    "missing_ticket_id": "falta identificador",
    "invalid_ticket_id": "identificador no válido",
    "invalid_date": "fecha no válida",
    "missing_client_company": "falta empresa cliente",
    "invalid_category": "categoría no válida o ausente",
    "invalid_description": "descripción vacía o demasiado corta",
    "invalid_title": "no se puede obtener un título",
    "invalid_agent_id": "identificador de agente no válido",
    "invalid_email": "email inválido o ausente",
    "invalid_status": "estado no válido",
    "closed_without_score": "ticket cerrado sin puntuación",
    "invalid_satisfaction_score": "puntuación fuera del rango permitido",
}


def seed_incidents(csv_path: Path, db_path: Optional[Path] = None) -> dict:
    if not csv_path.is_file():
        raise FileNotFoundError(f"No se encontró el CSV indicado: {csv_path}")

    db = SuppliersDB(db_path=db_path) if db_path else SuppliersDB()
    inserted = 0
    skipped_invalid = 0
    skipped_duplicate = 0
    issue_counts = {key: 0 for key in ISSUE_LABELS}
    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            required_columns = {
                "ticket_id", "date", "client_company", "category", "description",
                "agent_id", "status", "customer_email", "satisfaction_score",
            }
            if not required_columns.issubset(set(reader.fieldnames or [])):
                raise ValueError("El CSV no contiene las columnas requeridas para el análisis de incidencias.")

            for row_number, row in enumerate(reader, start=2):
                issues = validate_incident_csv_row(row)
                if issues:
                    skipped_invalid += 1
                    for issue in issues:
                        issue_counts[issue] += 1
                    safe_labels = ", ".join(ISSUE_LABELS[issue] for issue in issues)
                    print(f"Fila {row_number} omitida: {safe_labels}.")
                    continue

                key = source_key(row)
                if db.has_incident_import(key):
                    skipped_duplicate += 1
                    continue

                try:
                    fields, created_at = map_incident_row(row)
                    if validate_incident_fields(fields):
                        raise ValueError("Los campos transformados no cumplen el modelo de incidencia.")
                    incident = IncidentCreate.model_validate(fields)
                    created = db.create_incident(incident, created_at=created_at)
                    db.record_incident_import(key, created["id"])
                    inserted += 1
                except Exception:
                    # Do not print row values: the source row contains customer email.
                    print(f"Fila {row_number} omitida: no se pudo guardar la incidencia.")
                    skipped_invalid += 1

        print(
            "Carga finalizada: "
            f"{inserted} insertadas, {skipped_invalid} inválidas, "
            f"{skipped_duplicate} duplicadas."
        )
        issue_summary = ", ".join(
            f"{ISSUE_LABELS[key]}: {count}"
            for key, count in issue_counts.items()
            if count
        )
        if issue_summary:
            print(f"Reglas activadas: {issue_summary}.")
        return {
            "inserted": inserted,
            "skipped_invalid": skipped_invalid,
            "skipped_duplicate": skipped_duplicate,
            "issue_counts": issue_counts,
        }
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Carga idempotente de incidencias históricas.")
    parser.add_argument("csv", nargs="?", type=Path, default=REPO_ROOT / "incidents-nexova.csv")
    parser.add_argument("--db", type=Path, help="Ruta alternativa de TinyDB (útil para validar la carga).")
    args = parser.parse_args()
    try:
        seed_incidents(args.csv.resolve(), args.db.resolve() if args.db else None)
    except (FileNotFoundError, ValueError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
    except Exception:
        print("No se pudo completar la carga de incidencias.", file=sys.stderr)
        sys.exit(1)
