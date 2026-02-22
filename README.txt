Partner HTML Link Patch
======================

Purpose
-------
Updates partner-facing HTML (and any accompanying markdown/text in the same folder)
so all links/footers point to the canonical repo/site:

  Repo: https://github.com/PeterHiggins19/huf_core
  Docs: https://peterhiggins19.github.io/huf_core/

What it does
------------
- Creates a timestamped backup folder next to your partner_html folder.
- Rewrites old repo/site strings to the new canonical ones.
- Also fixes the common typo "PeterHIggins19" -> "PeterHiggins19".

How to run (PowerShell)
-----------------------
From the repo root:

  powershell -ExecutionPolicy Bypass -File scripts\patch_partner_html_links.ps1

Optional: also patch notes\legacy_md:

  powershell -ExecutionPolicy Bypass -File scripts\patch_partner_html_links.ps1 -IncludeLegacyNotes

After running
-------------
1) Verify no old strings remain:
   rg "huf_core_github_v1.1.8_no_inputs|PeterHIggins19|peterhiggins19.github.io/huf_core_github_v1.1.8_no_inputs" -n notes\partner_html

2) Commit the changes:
   git status
   git add notes\partner_html
   git commit -m "Update partner HTML links to canonical huf_core repo/site"

Generated: 2026-02-22T04:03:32
