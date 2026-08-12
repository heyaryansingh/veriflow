"""Tests for Expected Calibration Error.

ECE bins probabilities as (lower, upper]. The first bin used to exclude its
lower edge too, so a prediction of exactly 0.0 landed in no bin and was
dropped from the weighted average.
"""

import numpy as np
import pytest

from veriflow.evaluation.metrics import compute_calibration_ece


def test_hard_negatives_are_counted():
    """Half the samples predict 0.0 and are wrong; ECE must see them."""
    y_true = [1, 1, 0, 0]
    y_probs = [0.0, 0.0, 0.0, 0.0]

    # Every sample sits in the first bin with confidence 0 and accuracy 0.5.
    assert compute_calibration_ece(y_true, y_probs, n_bins=10) == pytest.approx(0.5)


def test_bin_weights_sum_to_one():
    """A perfectly calibrated set including 0.0 reports no error."""
    y_true = [0, 0, 1, 1]
    y_probs = [0.0, 0.0, 1.0, 1.0]

    assert compute_calibration_ece(y_true, y_probs, n_bins=10) == pytest.approx(0.0)


def test_ece_is_zero_for_a_calibrated_model():
    rng = np.random.default_rng(0)
    y_probs = rng.uniform(0.05, 0.95, size=5000)
    y_true = (rng.uniform(size=5000) < y_probs).astype(int)

    assert compute_calibration_ece(y_true, y_probs, n_bins=10) < 0.05


def test_ece_is_high_for_an_overconfident_model():
    y_true = [0] * 50 + [1] * 50
    y_probs = [1.0] * 50 + [0.0] * 50

    assert compute_calibration_ece(y_true, y_probs, n_bins=10) == pytest.approx(1.0)


def test_ece_accepts_two_dimensional_probabilities():
    y_true = [0, 1]
    y_probs = [[1.0, 0.0], [0.0, 1.0]]

    assert compute_calibration_ece(y_true, y_probs, n_bins=10) == pytest.approx(0.0)


def test_ece_of_an_empty_set_is_zero():
    assert compute_calibration_ece([], [], n_bins=10) == 0.0
