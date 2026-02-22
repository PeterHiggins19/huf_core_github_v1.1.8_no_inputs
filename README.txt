HUF polish bundle (v2, PowerShell 5.1 safe)
==========================================

Why v2
------
Windows PowerShell 5.1 can misread non-ASCII characters in .ps1 files unless they have a BOM.
This v2 script is ASCII-only and constructs mojibake patterns from codepoints.

Included
--------
- scripts/fix_readme_mojibake.ps1  (fix README encoding/punctuation safely)
- .gitattributes                   (exclude partner HTML from GitHub language stats)
- .gitignore.additions.txt         (lines to paste into your .gitignore)
- README_TOP_SUGGESTION.md         (suggested new README header with PROOF line)

Use
---
1) Unzip into your repo root (overwrite the existing script if present).
2) Run:
   powershell -ExecutionPolicy Bypass -File scripts\fix_readme_mojibake.ps1

3) Verify:
   rg "â|Ã¢|Â" README.md

4) Commit + push.

Generated: 2026-02-22T05:19:19
