# Spec — Member 1 (Data Owner)

**Project:** Appliances Energy Prediction
**Repo:** `ayesha-71131/Appliances-Energy-Prediction`
**Role:** Data Owner — raw data → prepared data → versioned data
**Current branch:** `data/initial-dataset` (exists, clean, cut from `dev`)

---

## 1. Purpose

Own the data lifecycle so that **anyone on the team can reproduce the exact dataset** with `git clone` + `dvc pull`, and so that no leakage or dirty data reaches model training.

## 2. Ownership

| Area | Files / artifacts |
|---|---|
| Dataset versioning | `.dvc/`, `.dvcignore`, `data/raw/energydata_complete.csv.dvc`, `data/raw/.gitignore`, DVC remote |
| Data validation | `src/data_checks.py`, `tests/test_data_checks.py` |
| Preparation + split | `src/prepare.py`, `tests/test_prepare.py`, `data/processed/` (DVC-tracked output) |
| Documentation | Dataset section of `README.md`, dataset/licence/source links in `REPORT.md`, temporal-split rationale |

Not owned (coordinate only): `train.py`, `evaluate.py`, `params.yaml` model params (Member 2); CI, pre-commit, release (Member 3).

## 3. Functional requirements

**FR1 — Dataset versioning**
- `data/raw/energydata_complete.csv` is never Git-tracked.
- Only the `.dvc` pointer, `.dvc/config` (no secrets), `.dvcignore` and `data/raw/.gitignore` are committed.
- Shared remote is DagsHub; `dvc push` succeeds; a teammate's `dvc pull` restores a file with shape `(19735, 29)`.

**FR2 — Credentials**
- User/token live only in `.dvc/config.local` (`--local`), never committed, never in the PR.

**FR3 — Data validation** (`src/data_checks.py`)
Callable from CLI and from CI. Checks:
- `date` parses and is monotonic increasing; 10-minute spacing gaps reported
- no duplicate timestamps
- no nulls
- expected columns and dtypes (29 columns)
- range checks (e.g. `Appliances >= 0`, humidity 0–100)
Exits non-zero on failure.

**FR4 — Preparation** (`src/prepare.py`)
- Reads path/params from `configs/params.yaml` (no hard-coded paths).
- Parses date, sorts by time, builds only **past-only** temporal features (hour, weekday, month; lags/rolling only if params request them and they use data ≤ T).
- Performs a **chronological** split: earliest → train, then validation, latest → test. No shuffling.
- Writes outputs to `data/processed/`.

**FR5 — Leakage rule**
Prediction time = T. Allowed: T, T-1, T-6, T-144… Forbidden: T+k, centered/forward rolling windows, scalers or statistics fit on val/test. Enforced by a unit test.

**FR6 — Data update (Phase 7)**
Produce a second dataset version (e.g. cleaned or with corrected rows) via `dvc add` on a new branch; show two commits with different `.dvc` hashes and that `git checkout <old> && dvc checkout` restores the old data.

## 4. Course-level obligations (Member 1's share)

- ≥ 2 merged PRs authored (`data/initial-dataset`, `data/update-cleaning`) plus code PRs where applicable
- ≥ 2 PR reviews of teammates' work
- ≥ 3 experiments recorded via `params.yaml` + `dvc exp` (suggested: baseline features; drop `rv1`/`rv2`; add temporal features)
- Participate in the deliberate merge conflict and its resolution
- Not the person who performs the final fresh-clone reproduction of the model if they trained it

## 5. Non-functional requirements

- Windows PowerShell + `uv` compatible; commands run via `uv run`.
- Every command in `README.md` works from a fresh clone.
- Commit messages follow team convention (`data: …`, `feat: …`, `test: …`, `docs: …`).
- Pre-commit hooks pass (ruff, nbstripout, large-file, secret scan).

## 6. Non-goals for `data/initial-dataset`

Cleaning, feature engineering, splitting, EDA, training, pipeline stages, CI. These belong to later branches.

## 7. Acceptance criteria (branch `data/initial-dataset`)

- [ ] CSV at `data/raw/energydata_complete.csv`, shape `(19735, 29)`, ~11.4 MB
- [ ] `git ls-files -- data/raw/energydata_complete.csv` → empty
- [ ] `git ls-files -- .dvc/config.local` → empty
- [ ] `dvc push` succeeds, `dvc status` clean
- [ ] `git diff --cached --name-only` lists only intended files (see plan step 9)
- [ ] PR `data/initial-dataset → dev`, reviewers Member 2 and Member 3
- [ ] Teammate fresh-clone `dvc pull` reproduces `(19735, 29)`; result posted in PR
- [ ] PR merged only after review + checks pass

## 8. Risks

| Risk | Mitigation |
|---|---|
| CSV or token committed | staged-file review + the `git ls-files` gates; pre-commit large-file/secret hooks |
| Teammate can't pull (no DagsHub access) | add collaborators to the DagsHub repo before asking for verification |
| Temporal leakage | chronological split, past-only features, dedicated unit test, checklist item in PR review |
| `dvc` missing from environment | add via `uv add --dev dvc` and coordinate with Member 3 (touches `pyproject.toml`/`uv.lock`) |
| Findings misrepresented | dataset is one low-energy building, ~4.5 months — state that limit in README/REPORT |
