import json

import numpy as np
import pandas as pd
import pytest

from src.evaluate import evaluate, regression_metrics
from src.train import build_model, load_split, train

TRAIN_PARAMS = {
    "model": "random_forest",
    "random_forest": {"n_estimators": 5, "max_depth": 3, "min_samples_leaf": 1},
    "hist_gradient_boosting": {"learning_rate": 0.1, "max_iter": 5, "max_depth": 3},
}


def _write_splits(data_dir):
    rng = np.random.default_rng(0)
    for name, n in (("train", 60), ("val", 20), ("test", 20)):
        df = pd.DataFrame(
            {
                "date": pd.date_range("2016-01-01", periods=n, freq="10min"),
                "x1": rng.normal(size=n),
                "x2": rng.normal(size=n),
            }
        )
        df["target"] = 2 * df["x1"] + df["x2"]
        df.to_csv(data_dir / f"{name}.csv", index=False)


def _config(tmp_path, model="random_forest"):
    return {
        "seed": 42,
        "train": {
            **TRAIN_PARAMS,
            "model": model,
            "data_dir": str(tmp_path),
            "model_path": str(tmp_path / "model.joblib"),
        },
        "evaluate": {"metrics_path": str(tmp_path / "metrics.json")},
    }


def test_load_split_drops_date_and_target(tmp_path):
    _write_splits(tmp_path)
    X, y = load_split(tmp_path, "train")
    assert list(X.columns) == ["x1", "x2"]
    assert len(X) == len(y) == 60


def test_unknown_model_raises():
    with pytest.raises(ValueError):
        build_model({**TRAIN_PARAMS, "model": "nope"}, seed=1)


def test_same_seed_gives_identical_predictions(tmp_path):
    _write_splits(tmp_path)
    X, y = load_split(tmp_path, "train")
    a = build_model(TRAIN_PARAMS, seed=7).fit(X, y).predict(X)
    b = build_model(TRAIN_PARAMS, seed=7).fit(X, y).predict(X)
    assert np.array_equal(a, b)


def test_regression_metrics_perfect_prediction():
    m = regression_metrics([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
    assert m == {"mae": 0.0, "rmse": 0.0, "r2": 1.0}


@pytest.mark.parametrize("model", ["random_forest", "hist_gradient_boosting"])
def test_train_then_evaluate_writes_metrics(tmp_path, model):
    _write_splits(tmp_path)
    config = _config(tmp_path, model)
    train(config)
    evaluate(config)
    metrics = json.loads((tmp_path / "metrics.json").read_text())
    assert metrics["model"] == model
    assert {"git_sha", "seed", "val", "test"} <= metrics.keys()
    assert set(metrics["test"]) == {"mae", "rmse", "r2"}
