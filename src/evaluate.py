"""Evaluate the trained model on the validation and test splits and write metrics.json.

Usage:
    python -m src.evaluate --params configs/params.yaml
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.train import load_config, load_split


def git_sha() -> str:
    """Current commit SHA, so every metrics file records the code that produced it."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def regression_metrics(y_true, y_pred) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
    }


def evaluate(config: dict) -> dict:
    train_params = config["train"]
    eval_params = config["evaluate"]
    bundle = joblib.load(train_params["model_path"])
    model, features = bundle["model"], bundle["features"]

    metrics: dict = {
        "git_sha": git_sha(),
        "model": train_params["model"],
        "seed": config["seed"],
    }
    for split in ("val", "test"):
        X, y = load_split(train_params["data_dir"], split)
        metrics[split] = regression_metrics(y, model.predict(X[features]))

    out = Path(eval_params["metrics_path"])
    out.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    return metrics


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Evaluate the trained model.")
    parser.add_argument("--params", default="configs/params.yaml")
    args = parser.parse_args(argv)
    evaluate(load_config(args.params))


if __name__ == "__main__":
    main()
