"""Seed the baseline database + HR-policy corpus with non-sensitive demo data.

The baseline agent holds NO employee PII and has NO employee-keyed data — just the
company holiday calendar and HR policy / FAQ articles. (The demo PR is what introduces
an employee-records table with name/email/SSN/salary.)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import db  # noqa: E402

# (id, tenant_id, name, date) — company-level holidays, no employee, no PII.
HOLIDAYS = [
    (1, 1, "New Year's Day", "2026-01-01"),
    (2, 1, "Independence Day", "2026-07-03"),
    (3, 1, "Thanksgiving", "2026-11-26"),
    (4, 1, "Winter Break", "2026-12-25"),
    (5, 2, "New Year's Day", "2026-01-01"),
    (6, 2, "Corporate Founders' Day", "2026-05-15"),
    (7, 2, "Winter Break", "2026-12-25"),
]

DOCS = [
    {"doc_id": "kb-t1-policy", "tenant_id": 1, "classification": "standard",
     "title": "PTO and benefits FAQ",
     "body": "Full-time staff accrue 1.5 PTO days/month. Request time off in the HR portal; your manager approves."},
    {"doc_id": "kb-t1-benefits", "tenant_id": 1, "classification": "standard",
     "title": "Benefits enrollment", "body": "Open enrollment runs each November. Update your contact email through HR support."},
    {"doc_id": "kb-t2-policy", "tenant_id": 2, "classification": "standard",
     "title": "Corporate onboarding FAQ", "body": "Corporate hires enroll in benefits within 30 days of their start date."},
]


def main() -> None:
    with db.connect() as con:
        con.executescript(db.SCHEMA)
        con.execute("DELETE FROM holidays")
        con.executemany(
            "INSERT INTO holidays (id, tenant_id, name, date) VALUES (?,?,?,?)", HOLIDAYS)
        con.commit()
    docs_dir = Path(__file__).resolve().parent / "docs"
    docs_dir.mkdir(exist_ok=True)
    for d in DOCS:
        (docs_dir / f"{d['doc_id']}.json").write_text(json.dumps(d, indent=2))
    print(f"seeded {len(HOLIDAYS)} company holidays, {len(DOCS)} HR policy docs (no PII)")


if __name__ == "__main__":
    main()
