import pandas as pd

from veriflow.data.missing_values import (
    check_missing_values,
    check_missing_values_for_path,
    check_missing_values_all_splits,
)


def test_check_missing_values_passes_when_under_threshold():
    df = pd.DataFrame({"a": [1, 2, 3, None], "b": [1, 2, 3, 4]})
    result = check_missing_values(df, threshold=0.5)

    assert result["passed"] is True
    assert result["flagged_columns"] == []
    assert result["column_rates"]["a"] == 0.25


def test_check_missing_values_flags_column_over_threshold():
    df = pd.DataFrame({"a": [None, None, None, 4], "b": [1, 2, 3, 4]})
    result = check_missing_values(df, threshold=0.5)

    assert result["passed"] is False
    assert result["flagged_columns"] == ["a"]


def test_check_missing_values_empty_dataframe():
    df = pd.DataFrame()
    result = check_missing_values(df)

    assert result["passed"] is True
    assert result["column_rates"] == {}


def test_check_missing_values_for_path_missing_file():
    result = check_missing_values_for_path("does_not_exist.csv")

    assert result["passed"] is False
    assert "Error loading dataset" in result["summary"]


def test_check_missing_values_all_splits(tmp_path):
    good_path = tmp_path / "train.csv"
    bad_path = tmp_path / "eval.csv"
    pd.DataFrame({"a": [1, 2, 3, 4]}).to_csv(good_path, index=False)
    pd.DataFrame({"a": [None, None, None, 4]}).to_csv(bad_path, index=False)

    result = check_missing_values_all_splits(
        {"train": good_path, "eval": bad_path}, threshold=0.5
    )

    assert result["passed"] is False
    assert result["splits"]["train"]["passed"] is True
    assert result["splits"]["eval"]["passed"] is False
