"""Incident management endpoints for Nexova."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import ValidationError

from ..database import SuppliersDB
from ..dependencies import get_current_user, get_db
from ..models import (
    IncidentBranchEnum,
    IncidentCategoryEnum,
    Incident,
    IncidentCreate,
    IncidentOriginEnum,
    IncidentStatusEnum,
    IncidentStatusUpdate,
)
from nexova_shared.incident_csv import validate_incident_field, validate_incident_fields

router = APIRouter(prefix="/api/incidents", tags=["incidents"])

TRANSITIONS = {
    IncidentStatusEnum.OPEN.value: {
        IncidentStatusEnum.IN_PROGRESS.value,
        IncidentStatusEnum.DISCARDED.value,
    },
    IncidentStatusEnum.IN_PROGRESS.value: {
        IncidentStatusEnum.RESOLVED.value,
        IncidentStatusEnum.DISCARDED.value,
    },
}


def _valid_filter(value: Optional[str], enum_type, field: str) -> Optional[str]:
    if value is None:
        return None
    try:
        return enum_type(value).value
    except ValueError:
        allowed = ", ".join(item.value for item in enum_type)
        raise HTTPException(status_code=400, detail={
            "message": f"Valor no válido para {field}.",
            "errors": [{"field": field, "message": f"Usa uno de estos valores: {allowed}."}],
        })


@router.post("", status_code=201, response_model=Incident)
async def create_incident(
    request: Request,
    _user: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db),
):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="El cuerpo de la solicitud debe ser JSON válido.")
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="El cuerpo de la solicitud debe ser un objeto JSON.")
    shared_errors = validate_incident_fields(payload)
    if shared_errors:
        raise HTTPException(
            status_code=400,
            detail={"message": "Revisa los campos obligatorios y sus valores.", "errors": shared_errors},
        )
    try:
        incident = IncidentCreate.model_validate(payload)
    except ValidationError as error:
        field_errors = [
            {"field": str(item["loc"][0]) if item.get("loc") else "general", "message": "Campo no permitido o valor inválido."}
            for item in error.errors()
        ]
        raise HTTPException(
            status_code=400,
            detail={"message": "Revisa los campos de la incidencia.", "errors": field_errors},
        )
    return db.create_incident(incident)


@router.get("", response_model=list[Incident])
def list_incidents(
    status: Optional[str] = Query(None),
    origin: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    _user: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db),
):
    return db.get_all_incidents(
        status=_valid_filter(status, IncidentStatusEnum, "status"),
        origin=_valid_filter(origin, IncidentOriginEnum, "origin"),
        branch=_valid_filter(branch, IncidentBranchEnum, "branch"),
        category=_valid_filter(category, IncidentCategoryEnum, "category"),
    )


@router.get("/summary")
def incident_summary(
    _user: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db),
):
    return db.get_incident_summary()


@router.get("/{incident_id}", response_model=Incident)
def get_incident(
    incident_id: int,
    _user: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db),
):
    incident = db.get_incident_by_id(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="No se encontró la incidencia.")
    return incident


@router.patch("/{incident_id}/status", response_model=Incident)
async def update_incident_status(
    incident_id: int,
    request: Request,
    _user: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db),
):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="El cuerpo de la solicitud debe ser JSON válido.")
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="El cuerpo de la solicitud debe ser un objeto JSON.")
    status_message = validate_incident_field("status", payload.get("status"))
    if status_message:
        raise HTTPException(status_code=400, detail={
            "message": "El estado indicado no es válido.",
            "errors": [{"field": "status", "message": status_message}],
        })
    try:
        update = IncidentStatusUpdate.model_validate(payload)
    except ValidationError:
        raise HTTPException(status_code=400, detail="Indica un estado válido para la incidencia.")

    incident = db.get_incident_by_id(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="No se encontró la incidencia.")

    allowed = TRANSITIONS.get(incident["status"], set())
    if update.status.value not in allowed:
        raise HTTPException(status_code=400, detail={
            "message": "No se pudo actualizar el estado.",
            "errors": [{"field": "status", "message": "La transición no está permitida para el ciclo de vida de esta incidencia."}],
        })
    return db.update_incident_status(incident_id, update.status.value)
