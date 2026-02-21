# Pinecone — namespace dominance audit (multi-tenant)

## Why it fits
Pinecone namespaces map 1:1 to `--regime-field namespace`.

## Entry point
- Export `id`, `score`, and `namespace` to JSONL
- Run the HUF coherence audit

## What to show
- when one namespace silently dominates
- how tightening tau changes concentration (proof line)
