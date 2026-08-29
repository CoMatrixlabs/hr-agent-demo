"""Company-level lookups for the HR assistant.

Deliberately holds NO employee data — just the company holiday calendar the assistant
needs to answer "when is the office closed?". Every read is parameterized and scoped to
the caller's business unit; there is no employee_id, name, SSN, salary, PTO-per-person,
or roster here — only a company-wide, non-personal table.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager

_DSN = os.environ.get("HR_AGENT_DSN", "hr_agent.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS holidays (
    id         INTEGER PRIMARY KEY,
    tenant_id  INTEGER NOT NULL,
    name       TEXT    NOT NULL,
    date       TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_holidays_tenant ON holidays(tenant_id);
"""


@contextmanager
def connect():
    con = sqlite3.connect(_DSN)
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()


def holiday_schedule(tenant_id: int) -> list[dict]:
    """Return the company holiday calendar for the caller's unit. Parameterized, no PII."""
    with connect() as con:
        cur = con.execute(
            "SELECT name, date FROM holidays WHERE tenant_id = ? ORDER BY date",
            (tenant_id,),
        )
        return [dict(row) for row in cur.fetchall()]
