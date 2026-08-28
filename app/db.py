"""Employee-records database access.

A thin SQLite layer holding employee records across multiple business units (tenants).
Every read is parameterized and scoped to the caller's business unit. Sensitive columns
(ssn, salary_cents) exist so the demo can show masking vs. leakage — real deployments
would tokenize these at rest.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager

_DSN = os.environ.get("HR_AGENT_DSN", "employee_records.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS employees (
    id            INTEGER PRIMARY KEY,
    tenant_id     INTEGER NOT NULL,
    name          TEXT    NOT NULL,
    email         TEXT    NOT NULL,
    ssn           TEXT    NOT NULL,
    salary_cents  INTEGER NOT NULL DEFAULT 0,
    manager       TEXT    NOT NULL,
    dept          TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_employees_tenant ON employees(tenant_id);
"""


@contextmanager
def connect():
    con = sqlite3.connect(_DSN)
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()


def find_employees(tenant_id: int, name_like: str) -> list[dict]:
    """Look up employees in ONE business unit by (partial) name. Parameterized + tenant-scoped."""
    with connect() as con:
        cur = con.execute(
            "SELECT id, tenant_id, name, email, ssn, salary_cents, manager, dept "
            "FROM employees WHERE tenant_id = ? AND name LIKE ? ORDER BY name",
            (tenant_id, f"%{name_like}%"),
        )
        return [dict(r) for r in cur.fetchall()]


def update_contact(tenant_id: int, employee_id: int, new_email: str) -> int:
    """Effectful write — used only behind the approval gate. Tenant-scoped."""
    with connect() as con:
        cur = con.execute(
            "UPDATE employees SET email = ? WHERE tenant_id = ? AND id = ?",
            (new_email, tenant_id, employee_id),
        )
        con.commit()
        return cur.rowcount
