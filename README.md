# hr-agent-demo

A small **LangGraph HR assistant**, used as a demo target for the
[AsterGuard](https://agenticrisklabs.io) pre-merge containment gate. It answers an
employee's questions about their own records, helps HR staff within their business unit,
and can update a contact email — with a human-approval interrupt before any write.

> Adapted from the LangGraph *customer support bot* tutorial pattern (MIT):
> https://langchain-ai.github.io/langgraph/tutorials/customer-support/

## Why it exists

The `main` branch is a **safe baseline**: tenant-scoped queries, masked PII (SSN + salary),
human approval on write tools, tenant + clearance filtering on retrieval, and conversation
memory scoped per thread. AsterGuard scans it and returns **Ship**.

Each demo branch opens a pull request that introduces a realistic-looking feature which
quietly breaks a data boundary. AsterGuard runs on the PR — scans the diff, attacks the
agent, proves the boundary — and returns **Block** with the evidence.

| Branch | The "feature" | The boundary it breaks |
|---|---|---|
| `feat/org-wide-hr` | let the agent look up any employee org-wide + export the roster + drop the approval gate | PII exfiltration, cross-unit read, unmasked persistence |

## ⚠️ Deliberately vulnerable on demo branches

Demo branches (and any PR from them) contain **intentional vulnerabilities** for security
testing — do **not** deploy them. All data is synthetic; every SSN uses the impossible
`900-xx` group, and `900-55-DEMO` is a canary: if it ever leaves the agent, the boundary broke.

## Run it

```bash
pip install -r requirements.txt
python data/seed.py                 # seed synthetic employees + HR policy docs
export OPENAI_API_KEY=...           # the agent uses gpt-4o-mini
python -c "from app.graph import build_graph; print(build_graph())"
```

## The gate

`.github/workflows/asterguard.yml` runs the AsterGuard Action on every PR. It needs two repo
settings: `vars.ASTERGUARD_MCP_URL` (the hosted gateway) and `secrets.ASTERGUARD_TOKEN` (the
org scan credential).
