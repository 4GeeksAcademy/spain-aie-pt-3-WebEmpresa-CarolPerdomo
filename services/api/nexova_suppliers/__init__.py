"""Nexova API package and monorepo shared-helper bootstrap."""

import sys
from pathlib import Path

SHARED_PYTHON = Path(__file__).resolve().parents[3] / "packages" / "shared" / "python"
if str(SHARED_PYTHON) not in sys.path:
    sys.path.insert(0, str(SHARED_PYTHON))
