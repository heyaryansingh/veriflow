"""ML metrics computation for Veriflow."""

from typing import Literal, Union
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score


def compute_accuracy(y_true, y_pred) -> float:
    """Computes accuracy score.
    
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        
    Returns:
        Accuracy score (float between 0 and 1)
    """
    if len(y_true) == 0:
        return 0.0
    
    return float(accuracy_score(y_true, y_pred))


def compute_f1(
    y_true,
    y_pred,
    average: Literal["binary", "macro", "micro", "weighted"] = "binary"
) -> float:
    """Computes F1 score.
    
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        average: Averaging strategy ('binary', 'macro', 'micro', 'weighted')
        
    Returns:
        F1 score (float between 0 and 1)
    """
    if len(y_true) == 0:
        return 0.0
    
    # Handle binary case with single class
    unique_classes = len(np.unique(y_true))
    if unique_classes == 1:
        # Single class: F1 is 1.0 if predictions match, 0.0 otherwise
        if np.array_equal(y_true, y_pred):
            return 1.0
        else:
            return 0.0
    
    # Use appropriate average for binary vs multiclass
    if unique_classes == 2 and average == "binary":
        return float(f1_score(y_true, y_pred, average="binary", zero_division=0))
    else:
        return float(f1_score(y_true, y_pred, average=average, zero_division=0))


def compute_roc_auc(
    y_true,
    y_scores,
    multi_class: Literal["raise", "ovr", "ovo"] = "raise"
) -> float:
    """Computes ROC-AUC score.
    
    Args:
        y_true: Ground truth labels
        y_scores: Predicted scores/probabilities
        multi_class: Strategy for multiclass ('raise', 'ovr', 'ovo')
        
    Returns:
        ROC-AUC score (float between 0 and 1)
    """
    if len(y_true) == 0:
        return 0.0
    
    y_true = np.array(y_true)
    y_scores = np.array(y_scores)
    
    # Handle binary case
    unique_classes = len(np.unique(y_true))
    if unique_classes == 1:
        # Single class: cannot compute ROC-AUC
        return 0.0
    
    if unique_classes == 2:
        # Binary: y_scores should be 1D (probability of positive class)
        if y_scores.ndim == 2:
            y_scores = y_scores[:, 1]  # Use positive class probabilities
        return float(roc_auc_score(y_true, y_scores))
    else:
        # Multiclass: y_scores should be 2D (probabilities for each class)
        if y_scores.ndim == 1:
            raise ValueError("Multiclass ROC-AUC requires 2D probability scores")
        return float(roc_auc_score(y_true, y_scores, multi_class=multi_class))


def compute_calibration_ece(y_true, y_probs, n_bins: int = 10) -> float:
    """Computes Expected Calibration Error (ECE).
    
    ECE measures how well-calibrated predicted probabilities are.
    Lower ECE indicates better calibration.
    
    Args:
        y_true: Ground truth binary labels (0 or 1)
        y_probs: Predicted probabilities (1D array for binary classification)
        n_bins: Number of bins for probability discretization
        
    Returns:
        Expected Calibration Error (float between 0 and 1)
    """
    if len(y_true) == 0:
        return 0.0
    
    y_true = np.array(y_true)
    y_probs = np.array(y_probs)
    
    # Handle binary classification only
    if y_probs.ndim > 1:
        # If 2D probabilities, use positive class
        y_probs = y_probs[:, 1] if y_probs.shape[1] > 1 else y_probs[:, 0]
    
    # Ensure probabilities are in [0, 1]
    y_probs = np.clip(y_probs, 0.0, 1.0)
    
    # Bin probabilities
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]
    
    ece = 0.0
    
    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
        # Find samples in this bin
        in_bin = (y_probs > bin_lower) & (y_probs <= bin_upper)
        prop_in_bin = in_bin.mean()
        
        if prop_in_bin > 0:
            # Accuracy in this bin
            accuracy_in_bin = y_true[in_bin].mean()
            # Average predicted probability in this bin
            avg_confidence_in_bin = y_probs[in_bin].mean()
            # Calibration error for this bin
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
    
    return float(ece)
