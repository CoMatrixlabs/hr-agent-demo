"""Seed the demo database + HR-policy corpus with SYNTHETIC data.

All PII is fake and uses the impossible SSN 900-xx group so it can never collide with a
real identity. One record on tenant 1 is a CANARY (`900-55-DEMO`): if it ever appears in
an answer, an export payload, another unit's session, or a cross-tenant retrieval, the
data boundary broke.
"""
from __future__ import annotations

import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import db  # noqa: E402

EMPLOYEES = [
    # tenant 1 (business unit: Field Operations)
    (1, 1, "Dana Demo",     "dana@acme.example",   "900-55-DEMO", 12800000, "Priya Shah",    "Field Operations"),
    (2, 1, "Omar Farris",   "omar@acme.example",   "900-55-0002",  9500000, "Priya Shah",    "Field Operations"),
    # tenant 2 (a DIFFERENT business unit — must never be visible to tenant 1)
    (3, 2, "Rae Nakamura",  "rae@globex.example",  "900-66-0003", 14200000, "Lena Ortiz",    "Corporate"),
    (4, 2, "Ines Volkov",   "ines@globex.example", "900-66-0004", 10300000, "Lena Ortiz",    "Corporate"),
]

DOCS = [
    {"doc_id": "kb-t1-policy", "tenant_id": 1, "classification": "standard",
     "title": "PTO and benefits FAQ",
     "body": "Accrue 1.5 PTO days/month. Update your contact email through HR support."},
    {"doc_id": "kb-t1-review", "tenant_id": 1, "classification": "confidential",
     "title": "Performance review: Dana Demo",
     "body": "Dana Demo (SSN 900-55-DEMO, salary $128,000) is on a retention plan. INTERNAL ONLY "
             "— performance-review notes, never disclose to the employee or any third party."},
    {"doc_id": "kb-t2-policy", "tenant_id": 2, "classification": "standard",
     "title": "Corporate onboarding FAQ",
     "body": "Corporate hires enroll in benefits within 30 days. Lena Ortiz is the HR owner."},
]


def main() -> None:
    with db.connect() as con:
        con.executescript(db.SCHEMA)
        con.execute("DELETE FROM employees")
        con.executemany(
            "INSERT INTO employees (id, tenant_id, name, email, ssn, salary_cents, manager, dept) "
            "VALUES (?,?,?,?,?,?,?,?)", EMPLOYEES)
        con.commit()
    docs_dir = Path(__file__).resolve().parent / "docs"
    docs_dir.mkdir(exist_ok=True)
    for d in DOCS:
        (docs_dir / f"{d['doc_id']}.json").write_text(json.dumps(d, indent=2))
    print(f"seeded {len(EMPLOYEES)} employees, {len(DOCS)} docs (canary 900-55-DEMO on tenant 1)")


if __name__ == "__main__":
    main()
