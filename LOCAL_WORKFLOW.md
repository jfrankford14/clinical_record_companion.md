# Local workspace → Git push quick-reference (safe version)

This is the authoritative path for every file in this environment. Follow the
checks below before staging or pushing so you always operate on the correct repo
worktree.

## 0) Verify you are in the repo root (not your home folder)

```bash
pwd
git rev-parse --show-toplevel   # should match the pwd output
git status -sb                  # should NOT list thousands of unrelated files
```

If `rev-parse` fails or prints your home directory, `cd` into the actual repo:

```bash
cd /workspace/clinical_record_companion.md
```

## 1) Detect alternate Git worktrees

Windows developers often clone with `git worktree`. List any additional working
copies and use the one that corresponds to your active branch:

```bash
git worktree list
```

If you see a path like `C:\Users\\<you>\\clinical-record-companion.wt-feature-unified`,
open that folder in your terminal/editor and run all git commands there.

## 2) Confirm branch and remote

```bash
git branch -vv
git remote -v
# Update the remote URL if necessary:
# git remote set-url origin https://github.com/<you>/clinical_record_companion.md.git
```

## 3) Stage, commit, push

```bash
git add -A
git commit -m "Finalize unified build: datasets, refs, tests, docs"
git push -u origin feature/unified-med-and-diabetes
```

After the first push, subsequent updates can use `git push` (no `-u` needed).

## 4) Verify on GitHub

In the GitHub UI, open the `feature/unified-med-and-diabetes` branch and confirm
you see the expected layout:

```
agent/  ccr/  data/  infra/  tests/  ui/  README.md  LOCAL_WORKFLOW.md
```

---

## If files landed outside the repo (fast rescue)

1. Search for mis-placed folders or files:

   ```powershell
   Get-ChildItem -Recurse -Directory -Path "C:\Users\<you>" -Filter "ccr" | Select -Expand FullName
   Get-ChildItem -Recurse -Filter "test_scenarios.py" -Path "C:\Users\<you>" | Select -Expand FullName
   Get-ChildItem -Recurse -Filter "MedicationKnowledgeBase.csv" -Path "C:\Users\<you>" | Select -Expand FullName
   ```

2. Copy them back into the tracked worktree (adjust paths as needed):

   ```powershell
   $SRC = "C:\Users\<you>\clinical-record-companion"                     # where Codex saved files
   $DST = "C:\Users\<you>\clinical-record-companion.wt-feature-unified"  # actual git worktree
   robocopy $SRC $DST /E /XD ".git" ".venv" "venv" "__pycache__"

   cd $DST
   git add -A
   git commit -m "Move Codex-created files into tracked worktree"
   git push -u origin feature/unified-med-and-diabetes
   ```

---

## Optional cleanup

* Keep a clean clone (e.g., `C:\dev\clinical_record_companion.md`) for future
  work to avoid confusing home-folder repos.
* If you accidentally ran git commands from your home directory, stop using that
  repo; switch back to the verified path above.

---

## Quick PR checklist (after push)

1. Open a "Compare & Pull Request" for `feature/unified-med-and-diabetes`.
2. Suggested title: **"Unify Diabetes + Med-Safety scenarios in single build"**.
3. Bullet summary: dataset packs, extended refs, scenario tests, no API changes.
