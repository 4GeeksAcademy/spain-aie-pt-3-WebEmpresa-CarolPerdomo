"""Run pytest-cov after preloading bcrypt for the local CPython 3.15 wheel."""

import sys

import bcrypt  # noqa: F401
import pytest


if __name__ == "__main__":
    raise SystemExit(pytest.main(sys.argv[1:]))
