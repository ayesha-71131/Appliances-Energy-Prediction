import pandas as pd

from src.eda import summarize_numeric


def test_summarize_numeric():
    df = pd.DataFrame({"target": [10, 20, 30, 40, 50]})

    result = summarize_numeric(df, "target")

    assert result["count"] == 5.0
    assert result["mean"] == 30.0
    assert result["median"] == 30.0
    assert result["min"] == 10.0
    assert result["max"] == 50.0
