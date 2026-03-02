# Patch: enforce "current documents supersede" for Books

Adds:
- notes/_org/current_sources.json
- scripts/sync_current_sources.py

Run dry-run:
```powershell
.\.venv\Scripts\python scripts\sync_current_sources.py
```

Apply:
```powershell
.\.venv\Scripts\python scripts\sync_current_sources.py --write
.\.venv\Scripts\python -m mkdocs build --strict
git add -A
git commit -m "Books: link to current_documents sources (handbook/reference)"
git push
.\.venv\Scripts\python -m mkdocs gh-deploy --force
```

If you later move the canonical DOCX to a new doc_id folder, update `notes/_org/current_sources.json`.
