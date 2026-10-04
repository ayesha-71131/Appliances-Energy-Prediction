# Plan — Member 1 (Data Owner)

Implements `spec.md`. Shell: PowerShell, repo root `C:\Users\mahnr\Appliances-Energy-Prediction`.
You are on `data/initial-dataset`, working tree clean.

---

## Part A — Branch `data/initial-dataset` (do now)

### Step 0 — Sync with dev
```powershell
git fetch --all --prune
git merge origin/dev          # "Already up to date" is fine
git log --oneline --graph --decorate -8
```

### Step 1 — Make sure DVC is available
```powershell
uv run dvc --version
```
If it fails:
```powershell
uv add --dev dvc
```
This changes `pyproject.toml` and `uv.lock`. Tell Member 3, and **stage those two files too** in Step 9 (they are part of this PR).

### Step 2 — Place and verify the data
Download `https://archive.ics.uci.edu/static/public/374/appliances+energy+prediction.zip`, extract, and put the CSV at:
```
data\raw\energydata_complete.csv
```
```powershell
New-Item -ItemType Directory -Force data\raw
uv run python -c "import pandas as pd; df=pd.read_csv('data/raw/energydata_complete.csv'); print(df.shape)"
```
Gate: must print `(19735, 29)`. Stop otherwise.

### Step 3 — Initialise DVC and track the file
```powershell
uv run dvc init
uv run dvc add data/raw/energydata_complete.csv
Get-Content data\raw\energydata_complete.csv.dvc
Get-Content data\raw\.gitignore        # should contain /energydata_complete.csv
```

### Step 4 — Create the DagsHub remote
1. On DagsHub: create/connect a repo for the project (connect the GitHub repo).
2. Add Member 2 and Member 3 as collaborators (they need access to pull).
3. Copy the DVC remote URL from **Remote → Data** (it looks like `https://dagshub.com/<user>/<repo>.dvc`). Don't guess it.
4. Create an access token in DagsHub settings.

```powershell
uv run dvc remote add -d origin <DAGSHUB_DVC_REMOTE_URL>
uv run dvc remote modify origin --local auth basic
uv run dvc remote modify origin --local user <DAGSHUB_USERNAME>
uv run dvc remote modify origin --local password <DAGSHUB_TOKEN>
uv run dvc remote list
```
`.dvc/config` (committed) holds only the URL. Credentials go in `.dvc/config.local`, which `dvc init` already git-ignores via `.dvc/.gitignore`. Confirm it anyway:
```powershell
git check-ignore -v .dvc/config.local
```

### Step 5 — Push data
```powershell
uv run dvc push
uv run dvc status
```

### Step 6 — Safety gates (all must print nothing)
```powershell
git ls-files -- data/raw/energydata_complete.csv
git ls-files -- .dvc/config.local
Select-String -Path .dvc\config -Pattern "password|token|user"
```

### Step 7 — README dataset section (small, same PR)
Add to `README.md`: source link, licence/usage note (UCI, CC BY 4.0), shape, 10-min sampling, date range, and the limitation (one low-energy house, ~4.5 months). Add the fetch instructions:
```
uv sync
uv run dvc pull
```

### Step 8 — Stage
```powershell
git add .dvc .dvcignore data/raw/.gitignore data/raw/energydata_complete.csv.dvc README.md
git add .gitignore                       # only if it changed
git add pyproject.toml uv.lock           # only if Step 1 changed them
git status
git diff --cached --name-only
git diff --cached
```
Nothing else should be staged. In particular NOT `energydata_complete.csv` or `config.local`.

### Step 9 — Commit and push
Pre-commit hooks will run if Member 3's config is merged; fix anything they report and re-stage.
```powershell
git commit -m "data: version raw Appliances Energy Prediction dataset with DVC"
git push -u origin data/initial-dataset
```

### Step 10 — Open PR
`data/initial-dataset → dev`, title `data: initial dataset versioning with DVC`, reviewers Member 2 + Member 3.
PR body: What / Changes / Dataset (file, shape, size, source) / Verification (paste gate outputs) / Review request (DVC config, ignore rules, credentials).

### Step 11 — Independent verification (Member 2 or 3)
```powershell
git clone https://github.com/ayesha-71131/Appliances-Energy-Prediction.git fresh-verify
cd fresh-verify
git checkout data/initial-dataset
uv sync
uv run dvc remote modify origin --local auth basic
uv run dvc remote modify origin --local user <THEIR_USERNAME>
uv run dvc remote modify origin --local password <THEIR_TOKEN>
uv run dvc pull
uv run python -c "import pandas as pd; print(pd.read_csv('data/raw/energydata_complete.csv').shape)"
```
Each teammate uses **their own** DagsHub credentials. They post the output in the PR.

### Step 12 — Merge and post-merge
Merge after: reviews done, comments addressed via new commits, verification posted, checks green.
```powershell
git switch dev
git pull origin dev
git ls-tree -r --name-only dev | Select-String "energydata"   # only the .dvc pointer
```
Also review two teammates' PRs (counts toward your 2 required reviews).

**Screenshots for REPORT.md:** shape output, `.dvc` pointer, `data/raw/.gitignore`, empty `git ls-files`, `dvc push`, PR page, teammate's `dvc pull`.

---

## Part B — Later branches (Member 1)

| # | Branch | Deliverable | PR checks |
|---|---|---|---|
| B1 | `feat/data-checks` | `src/data_checks.py` (FR3) + `tests/test_data_checks.py`; wire into `ci.yml` with Member 3 | tests pass; fails on injected bad row |
| B2 | `feat/prepare` | `src/prepare.py` (FR4/FR5): date parsing, sorting, past-only features, chronological split, reads `configs/params.yaml`; `tests/test_prepare.py` incl. a leakage test (features at T use no rows > T; train max date < val min date < test min date) | unit tests; no hard-coded paths |
| B3 | with Member 2: `feat/dvc-pipeline` | `prepare` stage in `dvc.yaml` (deps: CSV + `src/prepare.py`, params, outs: `data/processed/`) | `dvc repro` runs end to end |
| B4 | `data/update-cleaning` | second dataset version (FR6), new `.dvc` hash, `dvc push`, demonstrate rollback with `git checkout <old-sha> -- data/raw/*.dvc; dvc checkout` | before/after row counts and hashes in PR |
| B5 | `exp/m1-*` | 3 experiments via `params.yaml` + `dvc exp run` (baseline; drop `rv1/rv2`; add temporal features), compared with `dvc exp show` | metrics table in PR |
| B6 | shared | participate in the planned merge conflict (e.g. both edit `params.yaml`); resolve properly | conflict resolved in history |

Keep each PR small and single-purpose so the Git history shows your individual contribution.

---

## Part C — Definition of done for Member 1

- [ ] Part A merged to `dev`, teammate `dvc pull` confirmed
- [ ] B1–B4 merged, ≥ 2 PRs authored overall
- [ ] ≥ 2 reviews of others' PRs
- [ ] ≥ 3 experiments logged
- [ ] Data update version + rollback demonstrated
- [ ] README dataset section and REPORT dataset/source links are real URLs (no placeholders)
- [ ] Evidence screenshots collected

---

## Corrections vs. the earlier task plan

1. **`pyproject.toml` / `uv.lock`** may change if DVC has to be added, so they belong in the staged list.
2. **`.dvc/config.local`** is already ignored by DVC's own `.dvc/.gitignore`; the check is `git check-ignore`, not necessarily an edit to root `.gitignore`.
3. **Teammate verification needs their own DagsHub access and credentials**, otherwise `dvc pull` fails with an auth error, not a data error.
4. **Windows commands**: `Get-Content` / `Select-String` instead of `cat` / `grep`, and `uv run` prefixes.
5. **Rollback Case B** (CSV committed locally, unpushed): use `git reset --soft HEAD~1`, then unstage the CSV, rather than a vague "agreed procedure".
