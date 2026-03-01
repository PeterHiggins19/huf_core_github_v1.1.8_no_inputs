HUF-DOC: HUF.REL.DOCS.PAGE.GITHUB_FOR_BEGINNERS | HUF:1.1.8 | DOC:v0.1.0 | STATUS:release | LANE:release | RO:Peter Higgins
CODES: DOCS, GIT | ART: CM, AS, TR, EB | EVID:E0 | POSTURE:OP | WEIGHTS: OP=0.80 TOOL=0.20 PEER=0.00 | CAP: OP_MIN=0.51 TOOL_MAX=0.49 | CANON:docs/github_for_beginners.md

# GitHub for Beginners (no jargon)

You do **not** need Git to *use* HUF — a ZIP download works fine.  
But GitHub becomes useful once you want to **update** the project or **publish** changes.

## Option A — No Git (ZIP workflow)
- Download the release ZIP
- Unzip
- Run `START_HERE_WINDOWS.bat`
- If a newer release appears later, download the new ZIP and unzip over a new folder

## Option B — GitHub Desktop (simple “sync”)
GitHub Desktop is like a “Dropbox for code”:

### 1) Install GitHub Desktop
- Download from: `https://desktop.github.com/`
- Sign in with your GitHub account

### 2) Clone the repo
- File → Clone repository
- Paste the repo URL
- Choose a local folder (e.g. `D:\GitHub\HUF-Core\`)
- Click **Clone**

### 3) Pull updates
- Click **Fetch origin**  
- If it shows updates, click **Pull origin**

### 4) Make an edit and publish it
- Edit a file (e.g., `docs/index.md`)
- Back in GitHub Desktop, you’ll see the change
- Write a short message and click **Commit**
- Click **Push** (or **Sync**)

That’s it — your update is live on GitHub.

## GitHub Pages (your docs website)
GitHub Pages turns the `docs/` folder into a website (built with MkDocs).

If the repo has a Pages workflow enabled, you usually **don’t need to “activate buttons”** —
links work automatically, as long as the link paths are correct.

Common gotcha: in MkDocs, links should usually target pages like `start_here/` rather than GitHub file paths.

