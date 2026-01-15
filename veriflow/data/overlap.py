"""Overlap detection between dataset splits."""

from pathlib import Path
from typing import Union, Optional
import pandas as pd
from veriflow.data.loader import load_dataset


def find_overlap(
    df1: pd.DataFrame, 
    df2: pd.DataFrame, 
    key_columns: Optional[list[str]] = None
) -> dict:
    """Finds exact overlap between two DataFrames.
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame
        key_columns: Optional list of column names to use as keys for comparison.
                     If None, uses all columns for full row comparison.
        
    Returns:
        Dictionary with keys:
        - overlap_count: Number of overlapping rows
        - overlap_rows: DataFrame containing overlapping rows
        - overlap_percentage: Percentage of rows in df1 that overlap with df2
        - details: Human-readable description
    """
    if len(df1) == 0 or len(df2) == 0:
        return {
            "overlap_count": 0,
            "overlap_rows": pd.DataFrame(),
            "overlap_percentage": 0.0,
            "details": "One or both datasets are empty"
        }
    
    # Determine columns to use for comparison
    if key_columns is None:
        # Use all common columns
        common_cols = list(set(df1.columns) & set(df2.columns))
        if not common_cols:
            return {
                "overlap_count": 0,
                "overlap_rows": pd.DataFrame(),
                "overlap_percentage": 0.0,
                "details": "No common columns between datasets"
            }
    else:
        # Validate key columns exist in both DataFrames
        missing_in_df1 = [col for col in key_columns if col not in df1.columns]
        missing_in_df2 = [col for col in key_columns if col not in df2.columns]
        if missing_in_df1 or missing_in_df2:
            raise ValueError(
                f"Key columns missing: {missing_in_df1} in df1, {missing_in_df2} in df2"
            )
        common_cols = key_columns
    
    # Find overlap using merge
    # Use indicator to identify rows that exist in both
    merged = df1[common_cols].merge(
        df2[common_cols],
        how="inner",
        indicator=True
    )
    
    # Remove duplicates (same row appearing multiple times)
    overlap_rows = merged.drop_duplicates()
    overlap_count = len(overlap_rows)
    
    # Calculate percentage based on df1
    overlap_percentage = (overlap_count / len(df1) * 100) if len(df1) > 0 else 0.0
    
    # Build details string
    if overlap_count == 0:
        details = "No overlap detected"
    else:
        details = (
            f"Found {overlap_count} overlapping row(s) "
            f"({overlap_percentage:.2f}% of first dataset)"
        )
    
    return {
        "overlap_count": overlap_count,
        "overlap_rows": overlap_rows[common_cols] if overlap_count > 0 else pd.DataFrame(),
        "overlap_percentage": overlap_percentage,
        "details": details
    }


def check_train_eval_overlap(
    train_path: Union[str, Path],
    eval_path: Union[str, Path],
    key_columns: Optional[list[str]] = None
) -> dict:
    """Convenience function to check overlap between train and eval datasets.
    
    Args:
        train_path: Path to training dataset
        eval_path: Path to evaluation dataset
        key_columns: Optional list of column names to use as keys
        
    Returns:
        Dictionary with overlap details (same format as find_overlap)
    """
    try:
        train_df = load_dataset(train_path)
        eval_df = load_dataset(eval_path)
        return find_overlap(train_df, eval_df, key_columns)
    except Exception as e:
        return {
            "overlap_count": 0,
            "overlap_rows": pd.DataFrame(),
            "overlap_percentage": 0.0,
            "details": f"Error loading datasets: {e}"
        }


def check_all_splits_overlap(
    split_paths: dict[str, Union[str, Path]],
    key_columns: Optional[list[str]] = None
) -> dict:
    """Checks overlap between all pairs of dataset splits.
    
    Args:
        split_paths: Dictionary mapping split names to paths
                    (e.g., {"train": "train.csv", "eval": "eval.csv", "test": "test.csv"})
        key_columns: Optional list of column names to use as keys
        
    Returns:
        Dictionary with keys:
        - passed: bool indicating if no overlaps found
        - overlaps: List of dicts with split pairs and overlap details
        - summary: Human-readable summary string
    """
    overlaps = []
    split_names = list(split_paths.keys())
    
    # Check all pairs
    for i, split1_name in enumerate(split_names):
        for split2_name in split_names[i + 1:]:
            try:
                df1 = load_dataset(split_paths[split1_name])
                df2 = load_dataset(split_paths[split2_name])
                overlap_result = find_overlap(df1, df2, key_columns)
                
                if overlap_result["overlap_count"] > 0:
                    overlaps.append({
                        "split1": split1_name,
                        "split2": split2_name,
                        "overlap_count": overlap_result["overlap_count"],
                        "overlap_percentage": overlap_result["overlap_percentage"],
                        "details": overlap_result["details"]
                    })
            except Exception as e:
                overlaps.append({
                    "split1": split1_name,
                    "split2": split2_name,
                    "error": f"Failed to check overlap: {e}"
                })
    
    # Build summary
    if overlaps:
        summary = f"Found overlaps in {len(overlaps)} split pair(s)"
    else:
        summary = f"No overlaps detected between {len(split_names)} split(s)"
    
    return {
        "passed": len(overlaps) == 0,
        "overlaps": overlaps,
        "summary": summary
    }
