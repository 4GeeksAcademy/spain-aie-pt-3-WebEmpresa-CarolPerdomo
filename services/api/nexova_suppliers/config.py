import os
from pathlib import Path
from typing import Optional


def get_setting(name: str, default: Optional[str] = None) -> Optional[str]:
    """Read an OS environment variable, falling back to the repo's local .env."""
    value = os.getenv(name)
    if value:
        return value

    env_file = Path(__file__).resolve().parents[3] / ".env"
    try:
        lines = env_file.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return default

    for line in lines:
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        if entry.startswith("export "):
            entry = entry[7:].lstrip()
        key, separator, raw_value = entry.partition("=")
        if not separator or key.strip() != name:
            continue

        setting = raw_value.strip()
        if len(setting) >= 2 and setting[0] == setting[-1] and setting[0] in "\"'":
            setting = setting[1:-1]
        elif " #" in setting:
            setting = setting.split(" #", 1)[0].rstrip()
        return setting or default

    return default
