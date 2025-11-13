# Local workspace → Git push quick-reference (safe version)

## 0) Verify you’re in the repo root (not your home folder)

```bash
pwd
git rev-parse --show-toplevel   # should print the same path as pwd
git status -sb                  # should NOT list thousands of unrelated files
```

If `rev-parse` fails or prints your home directory, `cd` into the actual repo folder first.

## 1) Check for Git worktrees (Windows users commonly have these)

```bash
git worktree list
```

If you see paths like `...clinical-record-companion.wt-feature-unified`, run all Git ops **inside that folder**:

```bash
cd "C:\Users\<you>\clinical-record-companion.wt-feature-unified"
```

## 2) Confirm branch and remote

```bash
git branch -vv
git remote -v
# If needed:
# git remote set-url origin https://github.com/jfrankford14/clinical_record_companion.md
```

## 3) Stage, commit, push

```bash
git add -A
git commit -m "Finalize unified build: datasets, refs, tests, docs"
git push -u origin feature/unified-med-and-diabetes
```

## 4) Verify on GitHub

Open the branch and check you see:

```
ccr/  data/  tests/  agent/  infra/  README.md
```

---

## If Codex saved files outside the repo (fast rescue)

1. Find where Codex wrote them:

```powershell
Get-ChildItem -Recurse -Directory -Path "C:\Users\<you>" -Filter "ccr" | Select -Expand FullName
Get-ChildItem -Recurse -Filter "test_scenarios.py" -Path "C:\Users\<you>" | Select -Expand FullName
Get-ChildItem -Recurse -Filter "MedicationKnowledgeBase.csv" -Path "C:\Users\<you>" | Select -Expand FullName
```

2. Copy into the **correct worktree/repo root**, then commit:

```powershell
$SRC = "C:\Users\<you>\clinical-record-companion"                     # adjust to actual
$DST = "C:\Users\<you>\clinical-record-companion.wt-feature-unified"  # or your repo root
robocopy $SRC $DST /E /XD ".git" ".venv" "venv" "__pycache__"

cd $DST
git add -A
git commit -m "Move Codex-created files into tracked worktree"
git push -u origin feature/unified-med-and-diabetes
```

---

## Optional cleanup (to avoid future confusion)

* Make a clean clone in a dev folder (e.g., `C:\dev\clinical_record_companion.md`) and use that going forward.
* If you accidentally initialized a repo in your home folder, stop using it; only work in the clean clone.

---

## Quick PR checklist (after push)

* Open a **Compare & Pull Request** from `feature/unified-med-and-diabetes`.
* Title: “Unify Diabetes + Med-Safety scenarios in single build.”
* Bullets: added data pack, extended refs, tests, no API changes.

---

If you want, I can tailor the rescue commands with your exact paths; just paste the output of:

```
git worktree list
pwd
git rev-parse --show-toplevel
```
