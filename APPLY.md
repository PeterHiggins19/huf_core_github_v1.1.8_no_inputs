# Make-all-live patch (March 1, 2026)

This patch:
- Updates `mkdocs.yml` nav to include **Learning** and **Books** (and removes orphan warnings).
- Adds HUF headers (two-line coding) to core docs pages provided here.
- Adds `scripts/apply_huf_headers.py` to add headers across `docs/learning/**` and `docs/books/**` (manual run).
- Updates `scripts/doc_inventory.py` (placeholder DOC_ID ignored).

## Apply order
1) Paste over files in this zip to repo root.
2) Run header normalization (optional but recommended before publishing everything):
   ```powershell
   .\.venv\Scripts\python scripts\apply_huf_headers.py --root docs --write
   ```
3) Regenerate manifest:
   ```powershell
   .\.venv\Scripts\python scripts\doc_inventory.py --root . --write --merge
   ```
4) Verify docs:
   ```powershell
   .\.venv\Scripts\python -m mkdocs build --strict
   ```

