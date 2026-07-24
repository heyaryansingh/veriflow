import pandas as pd

from veriflow.data.duplicates import (
    check_duplicate_rows,
    check_duplicate_rows_for_path,
    check_duplicate_rows_all_splits,
)


def test_check_duplicate_rows_passes_when_under_threshold():
    df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [1, 2, 3, 4]})
    result = check_duplicate_rows(df, threshold=0.01)

    assert result["passed"] is True
    assert result["duplicate_count"] == 0
    assert result["duplicate_rate"] == 0.0


def test_check_duplicate_rows_flags_rate_over_threshold():
    df = pd.DataFrame({"a": [1, 1, 1, 4], "b": [1, 1, 1, 4]})
    result = check_duplicate_rows(df, threshold=0.1)

    assert result["passed"] is False
    assert result["duplicate_count"] == 2
    assert result["duplicate_rate"] == 0.5


def test_check_duplicate_rows_respects_subset_columns():
    df = pd.DataFrame({"id": [1, 2, 3], "text": ["hi", "hi", "bye"]})
    result = check_duplicate_rows(df, threshold=0.0, subset=["text"])

    assert result["passed"] is False
    assert result["duplicate_count"] == 1


def test_check_duplicate_rows_empty_dataframe():
    df = pd.DataFrame()
    result = check_duplicate_rows(df)

    assert result["passed"] is True
    assert result["duplicate_count"] == 0


def test_check_duplicate_rows_for_path_missing_file():
    result = check_duplicate_rows_for_path("does_not_exist.csv")

    assert result["passed"] is False
    assert "Error loading dataset" in result["summary"]


def test_check_duplicate_rows_all_splits(tmp_path):
    good_path = tmp_path / "train.csv"
    bad_path = tmp_path / "eval.csv"
    pd.DataFrame({"a": [1, 2, 3, 4]}).to_csv(good_path, index=False)
    pd.DataFrame({"a": [1, 1, 1, 4]}).to_csv(bad_path, index=False)

    result = check_duplicate_rows_all_splits(
        {"train": good_path, "eval": bad_path}, threshold=0.1
    )

    assert result["passed"] is False
    assert result["splits"]["train"]["passed"] is True
    assert result["splits"]["eval"]["passed"] is False
