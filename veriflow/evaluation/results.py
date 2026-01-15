"""Evaluation result storage for Veriflow."""

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
import json
import numpy as np
from veriflow.evaluation.metrics import (
    compute_accuracy,
    compute_f1,
    compute_roc_auc,
    compute_calibration_ece,
)
from veriflow.evaluation.bootstrap import (
    bootstrap_accuracy,
    bootstrap_f1,
    bootstrap_roc_auc,
)


@dataclass
class EvaluationResult:
    """Represents an ML evaluation result."""
    metrics: dict[str, float]  # Metric name -> value
    bootstrap_cis: dict[str, dict]  # Metric name -> CI dict
    metadata: dict  # Additional metadata (n_samples, seed, etc.)
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """Converts result to dictionary for JSON serialization."""
        return {
            "metrics": {k: float(v) for k, v in self.metrics.items()},
            "bootstrap_cis": {
                k: {kk: float(vv) if isinstance(vv, (int, float, np.number)) else vv
                    for kk, vv in v.items()}
                for k, v in self.bootstrap_cis.items()
            },
            "metadata": {
                k: float(v) if isinstance(v, (int, float, np.number)) else v
                for k, v in self.metadata.items()
            },
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "EvaluationResult":
        """Creates result from dictionary."""
        return cls(
            metrics=data["metrics"],
            bootstrap_cis=data["bootstrap_cis"],
            metadata=data["metadata"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


def save_evaluation_result(result: EvaluationResult, path: Union[str, Path]) -> None:
    """Saves evaluation result to JSON file.
    
    Args:
        result: EvaluationResult to save
        path: Path to save result (will be created in artifacts/ directory)
    """
    # Create artifacts directory if needed
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)
    
    # Create filename from path
    if isinstance(path, str):
        path = Path(path)
    
    # Create safe filename
    safe_name = str(path).replace("/", "_").replace("\\", "_").replace(":", "_")
    if not safe_name.endswith(".json"):
        safe_name += ".json"
    
    result_file = artifacts_dir / safe_name
    
    # Save result
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2)


def load_evaluation_result(path: Union[str, Path]) -> Optional[EvaluationResult]:
    """Loads evaluation result from JSON file.
    
    Args:
        path: Path to result file
        
    Returns:
        EvaluationResult if found, None otherwise
    """
    artifacts_dir = Path("artifacts")
    
    if isinstance(path, str):
        path = Path(path)
    
    # Create safe filename
    safe_name = str(path).replace("/", "_").replace("\\", "_").replace(":", "_")
    if not safe_name.endswith(".json"):
        safe_name += ".json"
    
    result_file = artifacts_dir / safe_name
    
    if not result_file.exists():
        return None
    
    try:
        with open(result_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return EvaluationResult.from_dict(data)
    except Exception:
        return None


def compute_evaluation_result(
    y_true,
    y_pred,
    y_scores=None,
    metrics=None,
    n_bootstrap: int = 1000,
    seed: Optional[int] = None
) -> EvaluationResult:
    """Computes complete evaluation result with metrics and bootstrap CIs.
    
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        y_scores: Predicted scores/probabilities (optional)
        metrics: List of metric names to compute (default: all available)
        n_bootstrap: Number of bootstrap samples (default: 1000)
        seed: Random seed for reproducibility (optional)
        
    Returns:
        EvaluationResult with metrics, bootstrap CIs, and metadata
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # Default metrics to compute
    if metrics is None:
        metrics = ["accuracy", "f1"]
        if y_scores is not None:
            metrics.extend(["roc_auc", "calibration_ece"])
    
    computed_metrics = {}
    computed_cis = {}
    
    # Compute metrics
    if "accuracy" in metrics:
        computed_metrics["accuracy"] = float(compute_accuracy(y_true, y_pred))
        computed_cis["accuracy"] = bootstrap_accuracy(
            y_true, y_pred, n_bootstrap=n_bootstrap, seed=seed
        )
    
    if "f1" in metrics:
        computed_metrics["f1"] = float(compute_f1(y_true, y_pred))
        computed_cis["f1"] = bootstrap_f1(
            y_true, y_pred, n_bootstrap=n_bootstrap, seed=seed
        )
    
    if y_scores is not None:
        y_scores = np.array(y_scores)
        
        if "roc_auc" in metrics:
            try:
                computed_metrics["roc_auc"] = float(compute_roc_auc(y_true, y_scores))
                computed_cis["roc_auc"] = bootstrap_roc_auc(
                    y_true, y_scores, n_bootstrap=n_bootstrap, seed=seed
                )
            except Exception:
                pass  # Skip if ROC-AUC cannot be computed
        
        if "calibration_ece" in metrics:
            try:
                computed_metrics["calibration_ece"] = float(
                    compute_calibration_ece(y_true, y_scores)
                )
                # ECE doesn't have bootstrap CI (it's already a calibration metric)
                computed_cis["calibration_ece"] = {
                    "metric_value": computed_metrics["calibration_ece"],
                    "ci_lower": computed_metrics["calibration_ece"],
                    "ci_upper": computed_metrics["calibration_ece"],
                    "confidence": 1.0
                }
            except Exception:
                pass
    
    # Create metadata
    metadata = {
        "n_samples": len(y_true),
        "seed": seed,
        "n_bootstrap": n_bootstrap,
    }
    
    return EvaluationResult(
        metrics=computed_metrics,
        bootstrap_cis=computed_cis,
        metadata=metadata,
        timestamp=datetime.now()
    )
