"""Distribution drift detection for Veriflow."""

from pathlib import Path
from typing import Union, Optional
import pandas as pd
import numpy as np
from veriflow.data.loader import load_dataset
from veriflow.data.fingerprint import compute_fingerprint, compare_fingerprints


def compute_distribution_stats(df: pd.DataFrame, column: str) -> dict:
    """Computes distribution statistics for a column.
    
    Args:
        df: pandas DataFrame
        column: Column name to analyze
        
    Returns:
        Dictionary with statistics:
        - For numeric: mean, std, min, max, percentiles (25, 50, 75), type
        - For categorical: value_counts (top 10), unique_count, type
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    series = df[column]
    dtype = str(series.dtype)
    
    # Check if numeric
    if pd.api.types.is_numeric_dtype(series):
        stats = {
            "type": "numeric",
            "mean": float(series.mean()) if not series.empty else 0.0,
            "std": float(series.std()) if not series.empty else 0.0,
            "min": float(series.min()) if not series.empty else None,
            "max": float(series.max()) if not series.empty else None,
            "percentile_25": float(series.quantile(0.25)) if not series.empty else None,
            "percentile_50": float(series.median()) if not series.empty else None,
            "percentile_75": float(series.quantile(0.75)) if not series.empty else None,
            "null_count": int(series.isna().sum()),
        }
    else:
        # Categorical
        value_counts = series.value_counts().head(10).to_dict()
        stats = {
            "type": "categorical",
            "value_counts": {str(k): int(v) for k, v in value_counts.items()},
            "unique_count": int(series.nunique()),
            "null_count": int(series.isna().sum()),
        }
    
    return stats


def compare_distributions(stats1: dict, stats2: dict, threshold: float = 0.1) -> dict:
    """Compares two distribution statistics.
    
    Args:
        stats1: First distribution stats
        stats2: Second distribution stats
        threshold: Relative change threshold (default 0.1 = 10%)
        
    Returns:
        Dictionary with keys:
        - changed: bool indicating if distribution changed significantly
        - delta: float representing the magnitude of change
        - details: Human-readable description
    """
    if stats1["type"] != stats2["type"]:
        return {
            "changed": True,
            "delta": 1.0,
            "details": f"Column type changed: {stats1['type']} -> {stats2['type']}"
        }
    
    if stats1["type"] == "numeric":
        # Compare numeric distributions using relative difference in mean and std
        mean1 = stats1["mean"]
        mean2 = stats2["mean"]
        std1 = stats1["std"]
        std2 = stats2["std"]
        
        # Avoid division by zero
        if mean1 == 0:
            mean_diff = abs(mean2) if mean2 != 0 else 0.0
        else:
            mean_diff = abs(mean1 - mean2) / abs(mean1)
        
        if std1 == 0:
            std_diff = abs(std2) if std2 != 0 else 0.0
        else:
            std_diff = abs(std1 - std2) / abs(std1)
        
        # Use maximum of mean and std differences
        delta = max(mean_diff, std_diff)
        changed = delta > threshold
        
        if changed:
            details = (
                f"Mean changed: {mean1:.2f} -> {mean2:.2f} "
                f"({mean_diff*100:.1f}%), "
                f"Std changed: {std1:.2f} -> {std2:.2f} ({std_diff*100:.1f}%)"
            )
        else:
            details = "No significant drift detected"
        
        return {
            "changed": changed,
            "delta": delta,
            "details": details
        }
    else:
        # Categorical: Use simple chi-square-like metric
        # Compare value counts distributions
        counts1 = stats1.get("value_counts", {})
        counts2 = stats2.get("value_counts", {})
        
        # Get all unique values
        all_values = set(counts1.keys()) | set(counts2.keys())
        
        if not all_values:
            return {
                "changed": False,
                "delta": 0.0,
                "details": "No values to compare"
            }
        
        # Compute total counts
        total1 = sum(counts1.values())
        total2 = sum(counts2.values())
        
        if total1 == 0 or total2 == 0:
            return {
                "changed": True,
                "delta": 1.0,
                "details": "One distribution is empty"
            }
        
        # Compute relative differences for each value
        max_diff = 0.0
        for value in all_values:
            count1 = counts1.get(value, 0)
            count2 = counts2.get(value, 0)
            
            prop1 = count1 / total1 if total1 > 0 else 0.0
            prop2 = count2 / total2 if total2 > 0 else 0.0
            
            diff = abs(prop1 - prop2)
            max_diff = max(max_diff, diff)
        
        changed = max_diff > threshold
        
        # Check unique count change
        unique_diff = abs(stats1["unique_count"] - stats2["unique_count"])
        if unique_diff > 0:
            changed = True
        
        if changed:
            details = (
                f"Value distribution changed (max diff: {max_diff*100:.1f}%), "
                f"unique count: {stats1['unique_count']} -> {stats2['unique_count']}"
            )
        else:
            details = "No significant drift detected"
        
        return {
            "changed": changed,
            "delta": max_diff,
            "details": details
        }


def check_drift_vs_baseline(
    current_path: Union[str, Path],
    baseline_path: Union[str, Path],
    threshold: float = 0.1,
    columns: Optional[list[str]] = None
) -> dict:
    """Checks distribution drift between current and baseline datasets.
    
    Args:
        current_path: Path to current dataset
        baseline_path: Path to baseline dataset
        threshold: Relative change threshold (default 0.1 = 10%)
        columns: Optional list of column names to check. If None, checks all common columns.
        
    Returns:
        Dictionary with keys:
        - passed: bool indicating if no drift detected
        - drifted_columns: List of dicts with column name and drift details
        - summary: Human-readable summary string
    """
    try:
        current_df = load_dataset(current_path)
        baseline_df = load_dataset(baseline_path)
    except Exception as e:
        return {
            "passed": False,
            "drifted_columns": [],
            "summary": f"Error loading datasets: {e}"
        }
    
    # Quick check: if datasets are identical (same fingerprint), skip drift check
    fp_current = compute_fingerprint(current_df)
    fp_baseline = compute_fingerprint(baseline_df)
    fingerprint_comp = compare_fingerprints(fp_baseline, fp_current)
    
    if not fingerprint_comp["changed"]:
        return {
            "passed": True,
            "drifted_columns": [],
            "summary": "Datasets are identical (no drift detected)"
        }
    
    # Determine columns to check
    common_columns = list(set(current_df.columns) & set(baseline_df.columns))
    if not common_columns:
        return {
            "passed": False,
            "drifted_columns": [],
            "summary": "No common columns between datasets"
        }
    
    if columns:
        # Filter to requested columns
        columns_to_check = [col for col in columns if col in common_columns]
    else:
        columns_to_check = common_columns
    
    drifted_columns = []
    
    # Check each column
    for column in columns_to_check:
        try:
            stats_current = compute_distribution_stats(current_df, column)
            stats_baseline = compute_distribution_stats(baseline_df, column)
            
            comparison = compare_distributions(stats_baseline, stats_current, threshold)
            
            if comparison["changed"]:
                drifted_columns.append({
                    "column": column,
                    "delta": comparison["delta"],
                    "details": comparison["details"]
                })
        except Exception as e:
            drifted_columns.append({
                "column": column,
                "error": f"Failed to compare: {e}"
            })
    
    # Build summary
    if drifted_columns:
        summary = f"Drift detected in {len(drifted_columns)} column(s)"
    else:
        summary = f"No drift detected in {len(columns_to_check)} column(s)"
    
    return {
        "passed": len(drifted_columns) == 0,
        "drifted_columns": drifted_columns,
        "summary": summary
    }
