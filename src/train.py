"""Train a regression model on the prepared training split.

Everything tunable (model choice, hyperparameters, seed) lives in configs/params.yaml.

Preprocessing note: both supported models are tree ensembles, which are invariant to
feature scaling, so no scaler is fitted. If a scale-sensitive model is added later, fit
its scaler on the training split only (inside a Pipeline) to avoid leakage.

Usage:
    python -m src.train --params configs/params.yaml
"""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
import yaml
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor

TARGET_COL = "target"
NON_FEATURE_COLS = ("date", TARGET_COL)
MODELS = ("random_forest", "hist_gradient_boosting")


def load_config(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_split(data_dir: str | Path, name: str) -> tuple[pd.DataFrame, pd.Series]:
    """Return (features, target) for one split. `date` is dropped: it is not a feature."""
    df = pd.read_csv(Path(data_dir) / f"{name}.csv")
    features = df.drop(columns=list(NON_FEATURE_COLS))
    return features, df[TARGET_COL]


def build_model(train_params: dict, seed: int):
    """Create the estimator named in params; every source of randomness gets `seed`."""
    name = train_params["model"]
    if name == "random_forest":
        return RandomForestRegressor(random_state=seed, n_jobs=1, **train_params[name])
    if name == "hist_gradient_boosting":
        return HistGradientBoostingRegressor(random_state=seed, **train_params[name])
    raise ValueError(f"Unknown model '{name}'. Choose one of {MODELS}")


def train(config: dict) -> Path:
    train_params = config["train"]
    X_train, y_train = load_split(train_params["data_dir"], "train")
    model = build_model(train_params, config["seed"])
    model.fit(X_train, y_train)

    out = Path(train_params["model_path"])
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": list(X_train.columns)}, out)
    print(f"trained {train_params['model']} on {len(X_train)} rows -> {out}")
    return out


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Train the model.")
    parser.add_argument("--params", default="configs/params.yaml")
    args = parser.parse_args(argv)
    train(load_config(args.params))


if __name__ == "__main__":
    main()
