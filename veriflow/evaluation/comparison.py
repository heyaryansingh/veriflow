"""Comparison of evaluation results for Veriflow."""

from pathlib import Path
from typing import Union
from veriflow.evaluation.results import EvaluationResult, load_evaluation_result


def is_significant_change(current_ci: dict, baseline_ci: dict) -> bool:
    """Checks if confidence intervals don't overlap (indicating significant change).
    
    Args:
        current_ci: Current result CI dict with ci_lower and ci_upper
        baseline_ci: Baseline result CI dict with ci_lower and ci_upper
        
    Returns:
        True if CIs don't overlap (significant change), False otherwise
    """
    current_lower = current_ci.get("ci_lower", 0.0)
    current_upper = current_ci.get("ci_upper", 0.0)
    baseline_lower = baseline_ci.get("ci_lower", 0.0)
    baseline_upper = baseline_ci.get("ci_upper", 0.0)
    
    # CIs don't overlap if current is completely above or below baseline
    return (current_lower > baseline_upper) or (current_upper < baseline_lower)


# Metrics where a smaller number is the better result. Everything else
# (accuracy, F1, ROC-AUC, ...) is treated as higher-is-better. Names are
# matched case-insensitively against these substrings, so "calibration_ece",
# "val_ece" and "test_brier" all resolve correctly.
LOWER_IS_BETTER_MARKERS = (
    "ece",
    "brier",
    "loss",
    "error",
    "mae",
    "mse",
    "rmse",
    "perplexity",
)


def is_lower_better(metric_name: str) -> bool:
    """Reports whether a smaller value of this metric is an improvement.

    Args:
        metric_name: Name of the metric, e.g. "accuracy" or "calibration_ece"

    Returns:
        True if lower values are better for this metric
    """
    name = str(metric_name).lower()
    tokens = set(name.replace("-", "_").split("_"))
    return any(
        marker in tokens or name == marker or name.endswith(marker)
        for marker in LOWER_IS_BETTER_MARKERS
    )


def compute_metric_delta(
    current_value: float,
    baseline_value: float,
    lower_is_better: bool = False
) -> dict:
    """Computes delta and relative change between two metric values.
    
    Args:
        current_value: Current metric value
        baseline_value: Baseline metric value
        lower_is_better: True for error-style metrics such as ECE or log loss,
            where a smaller value is the better result
        
    Returns:
        Dictionary with: delta (absolute change), relative_change (percentage), improved (bool)
    """
    delta = current_value - baseline_value
    
    if baseline_value == 0:
        relative_change = float("inf") if delta != 0 else 0.0
    else:
        relative_change = (delta / abs(baseline_value)) * 100
    
    improved = delta < 0 if lower_is_better else delta > 0
    
    return {
        "delta": delta,
        "relative_change": relative_change,
        "improved": improved
    }


def compare_results(
    current: EvaluationResult,
    baseline: EvaluationResult
) -> dict:
    """Compares current evaluation result against baseline.
    
    Args:
        current: Current evaluation result
        baseline: Baseline evaluation result
        
    Returns:
        Dictionary with keys:
        - passed: bool indicating if no regressions detected
        - comparisons: list of dicts with metric comparison details
        - summary: Human-readable summary string
    """
    comparisons = []
    
    # Compare each metric
    for metric_name in current.metrics.keys():
        if metric_name not in baseline.metrics:
            comparisons.append({
                "metric": metric_name,
                "status": "new",
                "details": "Metric not in baseline"
            })
            continue
        
        current_value = current.metrics[metric_name]
        baseline_value = baseline.metrics[metric_name]
        
        # Compute delta. Calibration error and other loss-style metrics move
        # the opposite way from accuracy, so a drop there is an improvement.
        delta_info = compute_metric_delta(
            current_value, baseline_value, lower_is_better=is_lower_better(metric_name)
        )
        
        # Check if significant change (using CIs if available)
        significant = False
        if metric_name in current.bootstrap_cis and metric_name in baseline.bootstrap_cis:
            current_ci = current.bootstrap_cis[metric_name]
            baseline_ci = baseline.bootstrap_cis[metric_name]
            significant = is_significant_change(current_ci, baseline_ci)
        
        # Determine status
        if significant:
            if delta_info["improved"]:
                status = "improved"
            else:
                status = "regressed"
        else:
            status = "unchanged"
        
        comparisons.append({
            "metric": metric_name,
            "status": status,
            "current_value": current_value,
            "baseline_value": baseline_value,
            "delta": delta_info["delta"],
            "relative_change": delta_info["relative_change"],
            "significant": significant,
            "details": f"{metric_name}: {baseline_value:.4f} -> {current_value:.4f} ({delta_info['relative_change']:+.2f}%)"
        })
    
    # Check for metrics in baseline but not in current
    for metric_name in baseline.metrics.keys():
        if metric_name not in current.metrics:
            comparisons.append({
                "metric": metric_name,
                "status": "missing",
                "details": "Metric missing in current result"
            })
    
    # Determine overall pass/fail
    # Pass if no regressions or missing metrics
    passed = all(
        comp["status"] not in ["regressed", "missing"]
        for comp in comparisons
    )
    
    # Build summary
    improved_count = sum(1 for comp in comparisons if comp["status"] == "improved")
    regressed_count = sum(1 for comp in comparisons if comp["status"] == "regressed")
    unchanged_count = sum(1 for comp in comparisons if comp["status"] == "unchanged")
    
    if regressed_count > 0:
        summary = f"Regression detected: {regressed_count} metric(s) regressed"
    elif improved_count > 0:
        summary = f"Improvement detected: {improved_count} metric(s) improved"
    else:
        summary = f"No significant changes: {unchanged_count} metric(s) unchanged"
    
    return {
        "passed": passed,
        "comparisons": comparisons,
        "summary": summary
    }


def compare_vs_baseline(
    current_path: Union[str, Path],
    baseline_path: Union[str, Path]
) -> dict:
    """Compares current evaluation result against baseline from files.
    
    Args:
        current_path: Path to current evaluation result JSON file
        baseline_path: Path to baseline evaluation result JSON file
        
    Returns:
        Comparison dict (same format as compare_results)
    """
    current = load_evaluation_result(current_path)
    baseline = load_evaluation_result(baseline_path)
    
    if current is None:
        return {
            "passed": False,
            "comparisons": [],
            "summary": f"Current result not found: {current_path}"
        }
    
    if baseline is None:
        return {
            "passed": False,
            "comparisons": [],
            "summary": f"Baseline result not found: {baseline_path}"
        }
    
    return compare_results(current, baseline)
