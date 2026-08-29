"""PTO-balance lookups for the HR assistant.

Deliberately holds NO employee PII — just a remaining-PTO figure the assistant needs to
answer "how many days do I have left?". Every read is parameterized and scoped to the
caller's business unit; there is no name, SSN, salary, or roster here.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager

_DSN = os.environ.get("HR_AGENT_DSN", "hr_agent.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS pto (
    employee_id    INTEGER PRIMARY KEY,
    tenant_id      INTEGER NOT NULL,
    days_remaining INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_pto_tenant ON pto(tenant_id);
"""


@contextmanager
def connect():
    con = sqlite3.connect(_DSN)
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()


def pto_balance(tenant_id: int, employee_id: int) -> dict | None:
    """Return remaining PTO days for ONE employee in the caller's unit. Parameterized, no PII."""
    with connect() as con:
        cur = con.execute(
            "SELECT days_remaining FROM pto WHERE tenant_id = ? AND employee_id = ?",
            (tenant_id, employee_id),
        )
        row = cur.fetchone()
        return dict(row) if row else None
