# Troubleshooting

**Updated:** 2026-02-17

This page collects the common “Windows reality” problems people hit when they’re new to Python tooling.

---

## 1) “.venv exists but commands run the wrong Python”

If you see paths like `miniconda3\Scripts\huf.exe`, you’re running a *global* install, not the repo venv.

Use the venv explicitly:

```powershell
.\.venv\Scripts\python -V
.\.venv\Scripts\huf --help
```

---

## 2) SSL certificate errors (CERTIFICATE_VERIFY_FAILED)

Symptoms:
- `ssl.SSLCertVerificationError: certificate verify failed`

Fix:
```powershell
.\.venv\Scripts\python -m pip install certifi
.\.venv\Scripts\python scripts\fetch_data.py --toronto --yes
```

If you are on a corporate network or behind a TLS-inspecting proxy, you may need to:
- download the dataset ZIP manually in a browser, then place the resulting CSV into the expected `cases\...\inputs\` folders

---

## 3) Toronto fetch gets HTTP 404

Use the default CKAN base:

- `https://open.toronto.ca/api/3/action`

Explicit override:

```powershell
.\.venv\Scripts\python scripts\fetch_data.py --toronto --yes --toronto-ckan https://open.toronto.ca/api/3/action
```

---

## 4) The Windows starter `.bat` prints weird characters

If you see “Γ£à” or similar, that’s just a console encoding mismatch.
It does **not** affect the run.

If you edited the `.bat` file, save it as:
- **ANSI** or **UTF-8** (not UTF-16)
- with normal Windows line endings

---

## 5) “File not found” for case inputs

Run fetch first:

```powershell
.\.venv\Scripts\python scripts\fetch_data.py --markham --toronto --yes
```

Then run the case commands.


## MkDocs command not found

If `mkdocs` isn’t on your PATH, run it via the repo venv:

```powershell
.\.venv\Scripts\python -m mkdocs serve
```
