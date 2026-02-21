# Troubleshooting

This page collects common “Windows reality” problems people hit when they’re new to Python tooling.

---

## “I typed `huf ...` and got `SyntaxError`”

If you see this:

- `>>> huf traffic ...`
- `SyntaxError: invalid syntax`

…you typed a **shell command inside Python**.

Fix:

1) exit Python: type `exit()` (or Ctrl+Z then Enter)
2) run the command in PowerShell:

```powershell
.\.venv\Scripts\huf --help
```

---

## “`make` is not recognized”

Windows does not ship `make`.

For the Planck download guide, use:

```powershell
.\.venv\Scripts\python scripts/fetch_data.py --planck-guide
```

---

## “.venv exists but commands run the wrong Python”

If you see paths like `miniconda3\Scripts\huf.exe`, you’re running a *global* install, not the repo venv.

Use the venv explicitly:

```powershell
.\.venv\Scripts\python -V
.\.venv\Scripts\huf --help
```

---

## MkDocs warning about “MkDocs 2.0”

Material for MkDocs currently expects a **pinned MkDocs 1.x** stack.

This repo pins:

- `mkdocs==1.6.1`
- `mkdocs-material==9.7.2`

Fix:

```powershell
.\.venv\Scripts\python -m pip install "mkdocs==1.6.1" "mkdocs-material==9.7.2"
```

Then always run:

```powershell
.\.venv\Scripts\python -m mkdocs serve
```

---

## SSL certificate errors (CERTIFICATE_VERIFY_FAILED)

Fix:

```powershell
.\.venv\Scripts\python -m pip install certifi
.\.venv\Scripts\python scripts/fetch_data.py --toronto --yes
```
