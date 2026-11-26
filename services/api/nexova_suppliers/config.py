"""Load the repository's ignored .env for local API runs without extra dependencies."""
import os
import re
from pathlib import Path
from typing import Optional


def get_setting(name: str, default: Optional[str] = None) -> Optional[str]:
    """Read a setting from the environment after the local .env is loaded."""
    return os.getenv(name, default)


def load_project_env() -> None:
    env_file = Path(__file__).resolve().parents[3] / ".env"
    if not env_file.is_file():
        return
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        name, separator, value = line.partition("=")
        name = name.strip()
        if not separator or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(name, value)
