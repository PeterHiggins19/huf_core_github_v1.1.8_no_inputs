# Repo hygiene (clean commits)

If you publish `site/` (MkDocs output) or `out/` (run artifacts) into git, GitHub will treat the repo like a static site
and the language bar becomes “mostly HTML”. This can reduce credibility for technical skimmers.

This repo is set up to **build** `site/` in GitHub Actions and publish it to Pages — you should not commit `site/`.

---

## Quick cleanup (recommended)

1) Ensure `.gitignore` includes:

- `site/`
- `out/`
- `*.egg-info/`
- `.venv/`

2) Remove generated folders from git tracking (keeps local files on disk):

```powershell
git rm -r --cached site out huf_core.egg-info
git commit -m "Repo hygiene: stop tracking generated outputs"
git push
```

If you don’t have `huf_core.egg-info` tracked, remove it from the command.

---

## Helper script (dry-run by default)

This repo includes a helper that detects tracked generated files and prints the exact commands:

```powershell
.\.venv\Scripts\python scripts/repo_cleanup.py
```

To apply automatically:

```powershell
.\.venv\Scripts\python scripts/repo_cleanup.py --apply
```

---

## Why this matters

- Cleaner diffs
- Fewer merge conflicts
- Correct GitHub language stats (shows Python, not HTML)
- Faster PR review (no “built site” noise)
