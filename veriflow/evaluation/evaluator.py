"""ML evaluation orchestrator for Veriflow."""

from pathlib import Path
from typing import Optional
import numpy as np
from veriflow.config import VeriflowConfig
from veriflow.evaluation.deterministic import get_evaluation_seed, set_deterministic_seed
from veriflow.evaluation.results import (
    compute_evaluation_result,
    save_evaluation_result,
    load_evaluation_result,
)
from veriflow.evaluation.comparison import compare_vs_baseline


def run_ml_evaluation(
    config: VeriflowConfig,
    y_true,
    y_pred,
    y_scores: Optional = None
) -> dict:
    """Orchestrates ML evaluation with metrics, bootstrap CIs, and baseline comparison.
    
    Args:
        config: VeriflowConfig object
        y_true: Ground truth labels
        y_pred: Predicted labels
        y_scores: Predicted scores/probabilities (optional)
        
    Returns:
        Dictionary with keys:
        - passed: bool indicating if evaluation passed (no regressions)
        - result: EvaluationResult object
        - comparison: Comparison dict if baseline exists, None otherwise
        - summary: Human-readable summary string
    """
    # Get seed from config
    seed = get_evaluation_seed(
        config.evaluation.seed if config.evaluation else None
    )
    
    # Set deterministic seed
    set_deterministic_seed(seed)
    
    # Compute evaluation result
    n_bootstrap = 1000  # Default, could be configurable
    result = compute_evaluation_result(
        y_true=y_true,
        y_pred=y_pred,
        y_scores=y_scores,
        n_bootstrap=n_bootstrap,
        seed=seed
    )
    
    # Save result
    result_path = Path("artifacts") / "evaluation_result.json"
    save_evaluation_result(result, result_path)
    
    # Compare against baseline if exists
    baseline_path = Path("artifacts") / "baseline_evaluation_result.json"
    comparison = None
    
    if baseline_path.exists():
        comparison = compare_vs_baseline(result_path, baseline_path)
        passed = comparison["passed"]
        summary = comparison["summary"]
    else:
        passed = True
        summary = f"Evaluation complete: {len(result.metrics)} metric(s) computed"
    
    return {
        "passed": passed,
        "result": result,
        "comparison": comparison,
        "summary": summary
    }
