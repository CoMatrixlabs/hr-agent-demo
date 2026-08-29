"""Seed the baseline database + HR-policy corpus with non-sensitive demo data.

The baseline agent holds NO employee PII — just a remaining-PTO figure per employee and
HR policy / FAQ articles. (The demo PR is what introduces an employee-records table with
name/email/SSN/salary.)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import db  # noqa: E402

# (employee_id, tenant_id, days_remaining) — no name, no SSN, no salary.
PTO = [
    (1, 1, 12),
    (2, 1, 5),
    (3, 2, 18),
    (4, 2, 9),
]

DOCS = [
    {"doc_id": "kb-t1-policy", "tenant_id": 1, "classification": "standard",
     "title": "PTO and benefits FAQ",
     "body": "Accrue 1.5 PTO days/month. Ask the assistant for your own remaining balance."},
    {"doc_id": "kb-t1-benefits", "tenant_id": 1, "classification": "standard",
     "title": "Benefits enrollment", "body": "Open enrollment runs each November. Update your contact email through HR support."},
    {"doc_id": "kb-t2-policy", "tenant_id": 2, "classification": "standard",
     "title": "Corporate onboarding FAQ", "body": "Corporate hires enroll in benefits within 30 days of their start date."},
]


def main() -> None:
    with db.connect() as con:
        con.executescript(db.SCHEMA)
        con.execute("DELETE FROM pto")
        con.executemany(
            "INSERT INTO pto (employee_id, tenant_id, days_remaining) VALUES (?,?,?)", PTO)
        con.commit()
    docs_dir = Path(__file__).resolve().parent / "docs"
    docs_dir.mkdir(exist_ok=True)
    for d in DOCS:
        (docs_dir / f"{d['doc_id']}.json").write_text(json.dumps(d, indent=2))
    print(f"seeded {len(PTO)} PTO rows, {len(DOCS)} HR policy docs (no PII)")


if __name__ == "__main__":
    main()
