"""Bootstrap confidence intervals for ML metrics."""

from typing import Callable, Optional, Union
import numpy as np
from veriflow.evaluation.metrics import (
    compute_accuracy,
    compute_f1,
    compute_roc_auc,
)
from veriflow.evaluation.deterministic import set_deterministic_seed


def bootstrap_metric(
    y_true,
    y_pred,
    metric_func: Callable,
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
    seed: Optional[int] = None
) -> dict:
    """Computes bootstrap confidence interval for a metric.
    
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        metric_func: Function that computes metric (y_true, y_pred) -> float
        n_bootstrap: Number of bootstrap samples (default: 1000)
        confidence: Confidence level (default: 0.95)
        seed: Random seed for reproducibility (optional)
        
    Returns:
        Dictionary with keys:
        - metric_value: Original metric value
        - ci_lower: Lower bound of confidence interval
        - ci_upper: Upper bound of confidence interval
        - confidence: Confidence level used
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    if len(y_true) == 0:
        return {
            "metric_value": 0.0,
            "ci_lower": 0.0,
            "ci_upper": 0.0,
            "confidence": confidence
        }
    
    # Set seed if provided
    if seed is not None:
        set_deterministic_seed(seed)
    
    # Compute original metric
    metric_value = float(metric_func(y_true, y_pred))
    
    # Bootstrap resampling
    n_samples = len(y_true)
    bootstrap_values = []
    
    for _ in range(n_bootstrap):
        # Resample with replacement
        indices = np.random.choice(n_samples, size=n_samples, replace=True)
        y_true_boot = y_true[indices]
        y_pred_boot = y_pred[indices]
        
        # Compute metric on resampled data
        try:
            boot_value = float(metric_func(y_true_boot, y_pred_boot))
            bootstrap_values.append(boot_value)
        except Exception:
            # Skip if metric computation fails (e.g., single class)
            continue
    
    if not bootstrap_values:
        # Fallback if all bootstrap samples failed
        return {
            "metric_value": metric_value,
            "ci_lower": metric_value,
            "ci_upper": metric_value,
            "confidence": confidence
        }
    
    # Compute confidence interval using percentiles
    alpha = 1 - confidence
    ci_lower = float(np.percentile(bootstrap_values, 100 * alpha / 2))
    ci_upper = float(np.percentile(bootstrap_values, 100 * (1 - alpha / 2)))
    
    return {
        "metric_value": metric_value,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "confidence": confidence
    }


def bootstrap_metrics(
    y_true,
    y_pred,
    metrics_dict: dict[str, Callable],
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
    seed: Optional[int] = None
) -> dict[str, dict]:
    """Computes bootstrap confidence intervals for multiple metrics.
    
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        metrics_dict: Dictionary mapping metric names to metric functions
        n_bootstrap: Number of bootstrap samples (default: 1000)
        confidence: Confidence level (default: 0.95)
        seed: Random seed for reproducibility (optional)
        
    Returns:
        Dictionary mapping metric names to bootstrap CI results
    """
    results = {}
    for metric_name, metric_func in metrics_dict.items():
        results[metric_name] = bootstrap_metric(
            y_true, y_pred, metric_func, n_bootstrap, confidence, seed
        )
    return results


def bootstrap_accuracy(
    y_true,
    y_pred,
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
    seed: Optional[int] = None
) -> dict:
    """Computes bootstrap confidence interval for accuracy.
    
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        n_bootstrap: Number of bootstrap samples (default: 1000)
        confidence: Confidence level (default: 0.95)
        seed: Random seed for reproducibility (optional)
        
    Returns:
        Dictionary with accuracy value and CI bounds
    """
    return bootstrap_metric(
        y_true, y_pred, compute_accuracy, n_bootstrap, confidence, seed
    )


def bootstrap_f1(
    y_true,
    y_pred,
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
    seed: Optional[int] = None,
    average: str = "binary"
) -> dict:
    """Computes bootstrap confidence interval for F1 score.
    
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        n_bootstrap: Number of bootstrap samples (default: 1000)
        confidence: Confidence level (default: 0.95)
        seed: Random seed for reproducibility (optional)
        average: Averaging strategy for F1 (default: 'binary')
        
    Returns:
        Dictionary with F1 value and CI bounds
    """
    def f1_func(y_t, y_p):
        return compute_f1(y_t, y_p, average=average)
    
    return bootstrap_metric(
        y_true, y_pred, f1_func, n_bootstrap, confidence, seed
    )


def bootstrap_roc_auc(
    y_true,
    y_scores,
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
    seed: Optional[int] = None
) -> dict:
    """Computes bootstrap confidence interval for ROC-AUC.
    
    Args:
        y_true: Ground truth labels
        y_scores: Predicted scores/probabilities
        n_bootstrap: Number of bootstrap samples (default: 1000)
        confidence: Confidence level (default: 0.95)
        seed: Random seed for reproducibility (optional)
        
    Returns:
        Dictionary with ROC-AUC value and CI bounds
    """
    y_true = np.array(y_true)
    y_scores = np.array(y_scores)
    
    if len(y_true) == 0:
        return {
            "metric_value": 0.0,
            "ci_lower": 0.0,
            "ci_upper": 0.0,
            "confidence": confidence
        }
    
    # Set seed if provided
    if seed is not None:
        set_deterministic_seed(seed)
    
    # Compute original metric
    metric_value = float(compute_roc_auc(y_true, y_scores))
    
    # Bootstrap resampling
    n_samples = len(y_true)
    bootstrap_values = []
    
    for _ in range(n_bootstrap):
        # Resample with replacement
        indices = np.random.choice(n_samples, size=n_samples, replace=True)
        y_true_boot = y_true[indices]
        y_scores_boot = y_scores[indices] if y_scores.ndim == 1 else y_scores[indices]
        
        # Compute metric on resampled data
        try:
            boot_value = float(compute_roc_auc(y_true_boot, y_scores_boot))
            bootstrap_values.append(boot_value)
        except Exception:
            continue
    
    if not bootstrap_values:
        return {
            "metric_value": metric_value,
            "ci_lower": metric_value,
            "ci_upper": metric_value,
            "confidence": confidence
        }
    
    # Compute confidence interval
    alpha = 1 - confidence
    ci_lower = float(np.percentile(bootstrap_values, 100 * alpha / 2))
    ci_upper = float(np.percentile(bootstrap_values, 100 * (1 - alpha / 2)))
    
    return {
        "metric_value": metric_value,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "confidence": confidence
    }
