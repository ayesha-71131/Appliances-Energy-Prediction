## What changed and why
<!-- Describe the changes you made and the motivation behind them -->

## Metrics (before → after)
<!-- Paste the dvc exp show table or a summary of the metrics -->

## Review checklist
- [ ] No data leakage (no target or future information in features)
- [ ] Splits are fixed; preprocessing fit on training data only
- [ ] No hardcoded paths; runs on a teammate's machine
- [ ] Seeds set for shuffling, initialisation and sampling
- [ ] Metric computed the way the team reports it
- [ ] dvc push done before git push (if data or models changed)

- [ ] Notebook restarted and run top to bottom (if notebooks changed)
- [ ] Style and naming (linter passes)
