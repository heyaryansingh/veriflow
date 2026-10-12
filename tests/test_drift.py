"""Tests for drift stats on boolean columns."""

import pandas as pd

from veriflow.data.drift import compute_distribution_stats


def test_bool_column_is_categorical():
    stats = compute_distribution_stats(pd.DataFrame({"x": [True, False, True]}), "x")
    assert stats["type"] == "categorical"
    assert stats["value_counts"] == {"True": 2, "False": 1}
