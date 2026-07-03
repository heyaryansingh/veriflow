"""Missing value rate detection for dataset splits."""

from pathlib import Path
from typing import Union
import pandas as pd
from veriflow.data.loader import load_dataset


def check_missing_values(
    df: pd.DataFrame,
    threshold: float = 0.5,
) -> dict:
    """Checks per-column null rates against a threshold.

    Args:
        df: pandas DataFrame to inspect
        threshold: Maximum allowed fraction of missing values per column (0-1)

    Returns:
        Dictionary with keys:
        - passed: bool, True if no column exceeds the threshold
        - column_rates: dict mapping column name to missing fraction
        - flagged_columns: list of columns exceeding the threshold
        - summary: Human-readable summary string
    """
    if len(df) == 0:
        return {
            "passed": True,
            "column_rates": {},
            "flagged_columns": [],
            "summary": "Dataset is empty, no missing value check performed",
        }

    column_rates = (df.isna().sum() / len(df)).to_dict()
    flagged_columns = [
        col for col, rate in column_rates.items() if rate > threshold
    ]

    if flagged_columns:
        summary = (
            f"{len(flagged_columns)} column(s) exceed missing value "
            f"threshold of {threshold:.0%}: {', '.join(flagged_columns)}"
        )
    else:
        summary = f"All columns within missing value threshold of {threshold:.0%}"

    return {
        "passed": len(flagged_columns) == 0,
        "column_rates": column_rates,
        "flagged_columns": flagged_columns,
        "summary": summary,
    }


def check_missing_values_for_path(
    path: Union[str, Path],
    threshold: float = 0.5,
) -> dict:
    """Convenience wrapper that loads a dataset from disk before checking.

    Args:
        path: Path to the dataset file
        threshold: Maximum allowed fraction of missing values per column (0-1)

    Returns:
        Dictionary with the same format as check_missing_values, or an
        error result if the dataset fails to load.
    """
    try:
        df = load_dataset(path)
        return check_missing_values(df, threshold)
    except Exception as e:
        return {
            "passed": False,
            "column_rates": {},
            "flagged_columns": [],
            "summary": f"Error loading dataset: {e}",
        }


def check_missing_values_all_splits(
    split_paths: dict[str, Union[str, Path]],
    threshold: float = 0.5,
) -> dict:
    """Checks missing value rates across all dataset splits.

    Args:
        split_paths: Dictionary mapping split names to paths
        threshold: Maximum allowed fraction of missing values per column (0-1)

    Returns:
        Dictionary with keys:
        - passed: bool, True if all splits pass
        - splits: dict mapping split name to its check_missing_values result
        - summary: Human-readable summary string
    """
    splits = {}
    for split_name, path in split_paths.items():
        splits[split_name] = check_missing_values_for_path(path, threshold)

    all_passed = all(result["passed"] for result in splits.values())
    failed_splits = [name for name, r in splits.items() if not r["passed"]]

    if all_passed:
        summary = f"All {len(splits)} split(s) passed missing value check"
    else:
        summary = f"Missing value check failed for split(s): {', '.join(failed_splits)}"

    return {
        "passed": all_passed,
        "splits": splits,
        "summary": summary,
    }
