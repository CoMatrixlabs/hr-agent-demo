"""Tools the HR assistant can call.

Read tools are tenant-scoped and mask PII (SSN + salary). Write tools are marked
sensitive so the graph routes them through a human-approval interrupt. There is
intentionally NO bulk-export tool in the baseline — exporting employee records
off-platform is not a capability we grant.
"""
from __future__ import annotations

import logging

from langchain_core.tools import tool

from . import db, rag
from .config import settings
from .pii import mask_record

logger = logging.getLogger("hr_agent.tools")

# The caller's identity is injected by the graph per request, never chosen by the model.
_CALLER = {"tenant_id": 1, "clearance": "standard"}


def set_caller(tenant_id: int, clearance: str = "standard") -> None:
    _CALLER["tenant_id"] = tenant_id
    _CALLER["clearance"] = clearance


@tool
def lookup_my_record(name: str) -> list[dict]:
    """Look up an employee's own record(s) by name to help answer their question.

    Returns records for the CALLER'S business unit only, with SSN + salary masked.
    """
    rows = db.find_employees(_CALLER["tenant_id"], name)
    logger.info("lookup_my_record name=%r -> %d rows (tenant=%s)", name, len(rows), _CALLER["tenant_id"])
    return [mask_record(r) for r in rows]


@tool
def search_policy(query: str) -> list[dict]:
    """Search HR policy docs for articles relevant to the employee's question."""
    return rag.search_docs(query, tenant_id=_CALLER["tenant_id"], clearance=_CALLER["clearance"])


@tool
def update_contact(employee_id: int, new_email: str) -> dict:
    """Update an employee's contact email. SENSITIVE: routed through human approval."""
    n = db.update_contact(_CALLER["tenant_id"], employee_id, new_email)
    return {"updated": n}


# Tools whose execution the graph must gate behind human approval.
SENSITIVE_TOOLS = {"update_contact"}

READ_TOOLS = [lookup_my_record, search_policy]
WRITE_TOOLS = [update_contact]
ALL_TOOLS = READ_TOOLS + WRITE_TOOLS
