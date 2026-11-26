"""Validation and safe mapping helpers for the legacy incident CSV."""

from datetime import date
import re
from typing import Dict, List, Optional, Tuple


VALID_CATEGORIES = {"TECHNICAL", "BILLING", "ACCESS", "HR_QUERY", "COMPLAINT"}
VALID_STATUSES = {"OPEN", "CLOSED", "DISCARDED"}
CATEGORY_MAP = {
    "TECHNICAL": "technical_failure",
    "BILLING": "process_error",
    "ACCESS": "technical_failure",
    "HR_QUERY": "process_error",
    "COMPLAINT": "client_complaint",
}
STATUS_MAP = {"OPEN": "open", "CLOSED": "resolved", "DISCARDED": "discarded"}
INCIDENT_STATUSES = ("open", "in_progress", "resolved", "discarded")
INCIDENT_ORIGINS = ("customer", "branch", "internal")
INCIDENT_BRANCHES = ("central", "valencia_operations", "miami_office", "remote")
INCIDENT_CATEGORIES = (
    "technical_failure", "process_error", "client_complaint", "candidate_issue",
    "staff_issue", "sla_breach", "data_quality", "other",
)


def validate_incident_field(field: str, value) -> Optional[str]:
    """Return a user-safe message for one Incident field, or None if it is valid."""
    if field in {"title", "description"}:
        if not isinstance(value, str) or not value.strip():
            return "Este campo es obligatorio."
        if field == "title" and len(value) > 120:
            return "El título debe tener 120 caracteres o menos."
    elif field == "category" and value not in INCIDENT_CATEGORIES:
        return "Selecciona una categoría permitida."
    elif field == "status" and value not in INCIDENT_STATUSES:
        return "Selecciona un estado permitido."
    elif field == "origin" and value not in INCIDENT_ORIGINS:
        return "Selecciona un origen permitido."
    elif field == "branch" and value not in INCIDENT_BRANCHES:
        return "Selecciona una sede permitida."
    return None


def validate_incident_fields(payload: Dict[str, object], required_fields=None) -> List[dict]:
    """Validate canonical Incident fields and return safe field/message pairs."""
    fields = required_fields or ("title", "description", "category", "status", "origin", "branch")
    errors = []
    for field in fields:
        message = validate_incident_field(field, payload.get(field))
        if message:
            errors.append({"field": field, "message": message})
    return errors


def validate_incident_csv_row(row: Dict[str, str]) -> List[str]:
    """Return safe rule identifiers only; never include input values in errors."""
    issues: List[str] = []
    ticket_id = (row.get("ticket_id") or "").strip()
    if not ticket_id:
        issues.append("missing_ticket_id")
    elif not re.fullmatch(r"NXV-\d{6}", ticket_id):
        issues.append("invalid_ticket_id")
    raw_date = (row.get("date") or "").strip()
    try:
        if len(raw_date) != 10 or date.fromisoformat(raw_date).isoformat() != raw_date:
            raise ValueError
    except ValueError:
        issues.append("invalid_date")
    if not (row.get("client_company") or "").strip():
        issues.append("missing_client_company")
    category = (row.get("category") or "").strip()
    if category not in VALID_CATEGORIES:
        issues.append("invalid_category")
    description = row.get("description") or ""
    if len(description.strip()) < 5:
        issues.append("invalid_description")
    if not description[:120].strip():
        issues.append("invalid_title")
    agent_id = (row.get("agent_id") or "").strip()
    if len(agent_id) != 6 or not agent_id.startswith("AGT-") or not agent_id[4:].isdigit():
        issues.append("invalid_agent_id")
    email = (row.get("customer_email") or "").strip()
    if not email or "@" not in email:
        issues.append("invalid_email")
    status = (row.get("status") or "").strip()
    if status not in VALID_STATUSES:
        issues.append("invalid_status")
    raw_score = (row.get("satisfaction_score") or "").strip()
    if status == "CLOSED" and not raw_score:
        issues.append("closed_without_score")
    if raw_score:
        try:
            score = int(raw_score)
            if str(score) != raw_score or not 1 <= score <= 5:
                raise ValueError
        except ValueError:
            issues.append("invalid_satisfaction_score")
    return issues


def source_key(row: Dict[str, str]) -> str:
    """Build a stable import key without persisting any customer contact data."""
    ticket_id = (row.get("ticket_id") or "").strip()
    if ticket_id:
        return f"ticket:{ticket_id}"
    title = (row.get("description") or "")[:120].strip()
    return f"fallback:{title}|{(row.get('date') or '').strip()}"


def map_incident_row(row: Dict[str, str]) -> Tuple[dict, str]:
    """Map an already validated CSV row to the public Incident fields and UTC time."""
    raw_date = row["date"].strip()
    return (
        {
            "title": row["description"][:120].strip(),
            "description": row["description"],
            "category": CATEGORY_MAP[row["category"].strip()],
            "status": STATUS_MAP[row["status"].strip()],
            "origin": "customer",
            "branch": "central",
        },
        f"{raw_date}T00:00:00+00:00",
    )
