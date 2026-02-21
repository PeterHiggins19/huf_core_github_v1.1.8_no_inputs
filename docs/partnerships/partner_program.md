# HUF partner program

HUF is an **artifact-first audit layer** for long-tail distributions in hierarchical systems (budgets, logs, exceptions, retrieval outputs).

This partner program exists to make integrations *predictable and repeatable*:

- **PR-first** (a proof artifact)
- **two commands** (Windows/Conda friendly)
- **four contract artifacts** (coherence map, active set, trace, error budget)
- **one proof line** (e.g., `items_to_cover_90pct 37 -> 12`)

---

## What partners get

### Technical deliverables

- A minimal integration that converts a partner’s output into **HUF JSONL** (`id`, `score`, plus a regime field like `namespace`/`collection`/`tenant`)
- A runnable example (no notebooks required)
- A dashboard command (`inspect_huf_artifacts.py`) that prints:
  - top regimes by `rho_global_post`
  - `items_to_cover_90pct`
  - discarded budget from `artifact_4_error_budget.json`

### Content deliverables

- A one-pager or “full picture” explainer (for a PR + email link)
- A case study page (problem → run → artifacts → interpretation)
- Optional: plots (coherence bars + concentration curve)

---

## Program tiers

### Tier 0 — Community example

**Goal:** get merged into the partner’s examples repo.

Deliverables:
- README + sample JSONL + 1–2 commands
- expected output section (copy/paste safe)
- license-compatible sample data

### Tier 1 — Integration listing

**Goal:** partner lists HUF in an integrations directory.

Deliverables:
- stable folder path + docs link
- “how it works” explainer
- screenshot-style artifact interpretation

### Tier 2 — Co-authored post

**Goal:** joint blog post explaining *why* (observability + governance), with a runnable demo.

Deliverables:
- blog outline + diagrams
- repeatable proof line (`items_to_cover_90pct X -> Y`)
- repo link + docs link

### Tier 3 — Strategic (enterprise / public sector)

**Goal:** pilot with real customer data and governance needs.

Deliverables:
- runbook (audit controls, trace retention, reporting)
- “governance pack” (trace report + discard ledger)
- optional: SOC2 / ISO-aligned mapping

---

## Partner targets

### Vector DBs

- Weaviate
- Qdrant
- Pinecone
- Milvus / Zilliz

### RAG orchestration

- LangChain
- LlamaIndex

### Evaluation / observability

- Arize Phoenix
- Weights & Biases
- Ragas

### Enterprise RAG platforms

- Glean
- Vectara

### Public sector + science

- Municipal budgets and logs (Markham / Toronto)
- Scientific computing validation (Planck 70 GHz)

---

## Operating rule

**PR first, email second.**  
A reviewable PR is the highest-leverage artifact: it reduces meetings and makes the ask concrete.
