"""Duplicate row detection for dataset splits."""

from pathlib import Path
from typing import Union
import pandas as pd
from veriflow.data.loader import load_dataset


def check_duplicate_rows(
    df: pd.DataFrame,
    threshold: float = 0.01,
    subset: list[str] | None = None,
) -> dict:
    """Checks the fraction of exact duplicate rows against a threshold.

    Args:
        df: pandas DataFrame to inspect
        threshold: Maximum allowed fraction of duplicate rows (0-1)
        subset: Optional list of columns to consider when identifying
                duplicates. Defaults to all columns.

    Returns:
        Dictionary with keys:
        - passed: bool, True if duplicate rate is within the threshold
        - duplicate_count: number of duplicate rows (beyond the first occurrence)
        - duplicate_rate: fraction of rows that are duplicates
        - summary: Human-readable summary string
    """
    if len(df) == 0:
        return {
            "passed": True,
            "duplicate_count": 0,
            "duplicate_rate": 0.0,
            "summary": "Dataset is empty, no duplicate row check performed",
        }

    duplicate_mask = df.duplicated(subset=subset, keep="first")
    duplicate_count = int(duplicate_mask.sum())
    duplicate_rate = duplicate_count / len(df)
    passed = duplicate_rate <= threshold

    if passed:
        summary = f"Duplicate row rate {duplicate_rate:.2%} within threshold of {threshold:.2%}"
    else:
        summary = (
            f"Duplicate row rate {duplicate_rate:.2%} exceeds threshold of "
            f"{threshold:.2%} ({duplicate_count} duplicate row(s))"
        )

    return {
        "passed": passed,
        "duplicate_count": duplicate_count,
        "duplicate_rate": duplicate_rate,
        "summary": summary,
    }


def check_duplicate_rows_for_path(
    path: Union[str, Path],
    threshold: float = 0.01,
    subset: list[str] | None = None,
) -> dict:
    """Convenience wrapper that loads a dataset from disk before checking.

    Args:
        path: Path to the dataset file
        threshold: Maximum allowed fraction of duplicate rows (0-1)
        subset: Optional list of columns to consider when identifying duplicates

    Returns:
        Dictionary with the same format as check_duplicate_rows, or an
        error result if the dataset fails to load.
    """
    try:
        df = load_dataset(path)
        return check_duplicate_rows(df, threshold, subset)
    except Exception as e:
        return {
            "passed": False,
            "duplicate_count": 0,
            "duplicate_rate": 0.0,
            "summary": f"Error loading dataset: {e}",
        }


def check_duplicate_rows_all_splits(
    split_paths: dict[str, Union[str, Path]],
    threshold: float = 0.01,
    subset: list[str] | None = None,
) -> dict:
    """Checks duplicate row rates across all dataset splits.

    Args:
        split_paths: Dictionary mapping split names to paths
        threshold: Maximum allowed fraction of duplicate rows (0-1)
        subset: Optional list of columns to consider when identifying duplicates

    Returns:
        Dictionary with keys:
        - passed: bool, True if all splits pass
        - splits: dict mapping split name to its check_duplicate_rows result
        - summary: Human-readable summary string
    """
    splits = {}
    for split_name, path in split_paths.items():
        splits[split_name] = check_duplicate_rows_for_path(path, threshold, subset)

    all_passed = all(result["passed"] for result in splits.values())
    failed_splits = [name for name, r in splits.items() if not r["passed"]]

    if all_passed:
        summary = f"All {len(splits)} split(s) passed duplicate row check"
    else:
        summary = f"Duplicate row check failed for split(s): {', '.join(failed_splits)}"

    return {
        "passed": all_passed,
        "splits": splits,
        "summary": summary,
    }
