# Link hygiene: "current documents override" updates

This adds:
- `scripts/link_hygiene_current.py`

Run (dry-run):
```powershell
.\.venv\Scripts\python scripts\link_hygiene_current.py
```

Apply changes + write report:
```powershell
.\.venv\Scripts\python scripts\link_hygiene_current.py --write
```

Then verify:
```powershell
.\.venv\Scripts\python -m mkdocs build --strict
```

If you publish:
```powershell
.\.venv\Scripts\python -m mkdocs gh-deploy --force
```
