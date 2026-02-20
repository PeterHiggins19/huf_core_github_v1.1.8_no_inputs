# Doc catalog

This folder is maintained by:

- `scripts/catalog_docs.py`

Files:

- `docs_current.json` — all Markdown files currently under `docs/`
- `docs_removed.json` — “tombstone list” (docs that existed before but are now missing)
- `nav_files.json` — Markdown files referenced in `mkdocs.yml` nav
- `orphans.json` — docs present but not in nav
- `missing_in_docs.json` — docs referenced by nav but missing on disk

Why this exists:

- Keeps `mkdocs build --strict` bulletproof
- Prevents accidental loss of docs during overlay merges
- Makes it obvious when new pages were added but never linked into the learning path
