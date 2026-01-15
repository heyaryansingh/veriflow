"""Evaluation module for Veriflow."""

from veriflow.evaluation.metrics import (
    compute_accuracy,
    compute_f1,
    compute_roc_auc,
    compute_calibration_ece,
)
from veriflow.evaluation.deterministic import (
    set_deterministic_seed,
    get_evaluation_seed,
    ensure_deterministic,
)
from veriflow.evaluation.bootstrap import (
    bootstrap_metric,
    bootstrap_metrics,
    bootstrap_accuracy,
    bootstrap_f1,
    bootstrap_roc_auc,
)

__all__ = [
    "compute_accuracy",
    "compute_f1",
    "compute_roc_auc",
    "compute_calibration_ece",
    "set_deterministic_seed",
    "get_evaluation_seed",
    "ensure_deterministic",
    "bootstrap_metric",
    "bootstrap_metrics",
    "bootstrap_accuracy",
    "bootstrap_f1",
    "bootstrap_roc_auc",
]
