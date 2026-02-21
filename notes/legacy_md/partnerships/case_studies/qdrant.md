# Qdrant — collection/payload coherence audit

## Why it fits
Qdrant payload fields (e.g., `collection`, `source`, `tenant`) are natural regime fields for HUF.

## Entry point
- Export Qdrant search results to JSONL (`id`, `score`, plus regime field)
- Run HUF coherence audit on the export

## What to show
- `rho_global_post` by collection/payload regime
- `items_to_cover_90pct` as a “risk of stale top chunks” metric
- `artifact_4_error_budget.json` as a declared discard ledger
