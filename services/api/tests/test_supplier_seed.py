import os
from pathlib import Path
from uuid import uuid4

os.environ.setdefault("SECRET_KEY", "test-only-secret-key-for-seed-tests")

from nexova_suppliers.database import SuppliersDB
from nexova_suppliers.seed import SUPPLIERS_SEED, seed_suppliers


def test_seed_loads_briefing_suppliers_once_and_persists(capsys):
    db_path = Path(__file__).resolve().parents[1] / "data" / f"supplier-seed-test-{uuid4().hex}.json"
    try:
        _verify_seed_is_idempotent(db_path, capsys)
    finally:
        db_path.unlink(missing_ok=True)


def _verify_seed_is_idempotent(db_path: Path, capsys):
    seed_suppliers(db_path)
    first_output = capsys.readouterr().out
    assert f"{len(SUPPLIERS_SEED)} proveedores insertados" in first_output

    db = SuppliersDB(db_path)
    try:
        seeded = db.get_all_suppliers()
        assert len(seeded) == len(SUPPLIERS_SEED)
        assert {supplier["name"] for supplier in seeded} == {row["name"] for row in SUPPLIERS_SEED}
        assert all(supplier.get("updated_at") for supplier in seeded)
    finally:
        db.close()

    seed_suppliers(db_path)
    second_output = capsys.readouterr().out
    assert "0 proveedores insertados" in second_output

    reopened = SuppliersDB(db_path)
    try:
        assert len(reopened.get_all_suppliers()) == len(SUPPLIERS_SEED)
    finally:
        reopened.close()
