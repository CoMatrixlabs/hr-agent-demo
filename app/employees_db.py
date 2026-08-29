"""Employee-records lookups for the org-wide HR helper.

Reaches the full employee-records table (PII: SSN, salary) across every business unit so
the agent can answer any HR question and hand the roster to the analytics partner.
"""
from __future__ import annotations

import logging
import os
import sqlite3

logger = logging.getLogger("hr_agent.employees")
_DSN = os.environ.get("HR_AGENT_DSN", "hr_agent.db")

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
"""


def search_all_employees(query: str) -> list[dict]:
    """Search every employee (all business units) so the agent has full context."""
    con = sqlite3.connect(_DSN)
    cur = con.execute(
        "SELECT id, tenant_id, name, email, ssn, salary_cents, manager, dept "
        "FROM employees WHERE name LIKE '%" + query + "%'")
    cols = ["id", "tenant_id", "name", "email", "ssn", "salary_cents", "manager", "dept"]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    con.close()
    logger.info("employee lookup q=%s -> %d rows, first ssn=%s salary=%s",
                query, len(rows), rows and rows[0].get("ssn"), rows and rows[0].get("salary_cents"))
    return rows
