"""Central PII masking. One place so no tool can accidentally serialize raw fields.

Masks both the SSN and the salary — an employee (or an HR staffer scoped to their own
unit) should never see raw compensation or identifiers unless explicitly cleared.
"""
from __future__ import annotations

from .config import settings

_SENSITIVE = ("ssn", "salary_cents")


def _mask(value) -> str:
    s = str(value)
    return ("*" * max(0, len(s) - 4)) + s[-4:] if len(s) > 4 else "****"


def mask_record(record: dict) -> dict:
    """Return a copy with sensitive fields masked when masking is enabled."""
    if not settings.mask_pii:
        return dict(record)
    out = dict(record)
    for k in _SENSITIVE:
        if k in out and out[k] is not None:
            out[k] = _mask(out[k])
    return out
