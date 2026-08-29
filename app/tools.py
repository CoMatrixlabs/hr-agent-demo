"""Tools the HR assistant can call.

Baseline capability is intentionally narrow and PII-free: search the HR policy / FAQ
knowledge base and report the caller's OWN remaining PTO. No employee records, no
roster, no data export, no writes. That keeps the agent's data boundary trivial —
which is the point: the demo PR is what wires it to employee data and breaks the boundary.
"""
from __future__ import annotations

from langchain_core.tools import tool

from . import db, rag

# The caller's identity is injected by the graph per request, never chosen by the model.
_CALLER = {"tenant_id": 1, "employee_id": 1, "clearance": "standard"}


def set_caller(tenant_id: int, employee_id: int = 1, clearance: str = "standard") -> None:
    _CALLER["tenant_id"] = tenant_id
    _CALLER["employee_id"] = employee_id
    _CALLER["clearance"] = clearance


@tool
def search_policy(query: str) -> list[dict]:
    """Search HR policy docs / FAQ for articles relevant to the employee's question."""
    return rag.search_docs(query, tenant_id=_CALLER["tenant_id"], clearance=_CALLER["clearance"])


@tool
def pto_balance(employee_id: int) -> dict:
    """Report remaining PTO days for the CALLER's own record only (no other employees, no PII)."""
    if employee_id != _CALLER["employee_id"]:
        return {"error": "you can only view your own PTO balance"}
    row = db.pto_balance(_CALLER["tenant_id"], _CALLER["employee_id"])
    return row or {"error": "no PTO record found"}


# No sensitive tools in the baseline; the graph gates any that are added here.
SENSITIVE_TOOLS: set[str] = set()

READ_TOOLS = [search_policy, pto_balance]
WRITE_TOOLS: list = []
ALL_TOOLS = READ_TOOLS + WRITE_TOOLS
