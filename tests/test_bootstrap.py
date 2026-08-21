"""Tests for bootstrap confidence intervals."""

import random

import numpy as np
import pytest

from veriflow.evaluation.bootstrap import (
    bootstrap_accuracy,
    bootstrap_f1,
    bootstrap_metric,
    bootstrap_metrics,
    bootstrap_roc_auc,
)
from veriflow.evaluation.metrics import compute_accuracy


@pytest.fixture
def labels():
    rng = np.random.default_rng(0)
    y_true = rng.integers(0, 2, 200)
    # ~80% agreement so the CI is a real interval, not a degenerate point
    flip = rng.random(200) < 0.2
    y_pred = np.where(flip, 1 - y_true, y_true)
    return y_true, y_pred


def test_ci_brackets_the_point_estimate(labels):
    y_true, y_pred = labels
    result = bootstrap_accuracy(y_true, y_pred, n_bootstrap=200, seed=1)

    assert result["ci_lower"] <= result["metric_value"] <= result["ci_upper"]
    assert result["ci_lower"] < result["ci_upper"]
    assert result["confidence"] == 0.95


def test_same_seed_reproduces_bounds(labels):
    y_true, y_pred = labels
    first = bootstrap_accuracy(y_true, y_pred, n_bootstrap=200, seed=7)
    second = bootstrap_accuracy(y_true, y_pred, n_bootstrap=200, seed=7)

    assert first == second


def test_seeding_does_not_leak_into_global_rng(labels):
    """Regression: bootstrap called set_deterministic_seed, which reseeded the
    global numpy/random/torch generators out from under the caller."""
    y_true, y_pred = labels

    np.random.seed(1234)
    random.seed(1234)
    expected_np = np.random.rand()
    expected_py = random.random()

    np.random.seed(1234)
    random.seed(1234)
    bootstrap_accuracy(y_true, y_pred, n_bootstrap=50, seed=99)

    assert np.random.rand() == expected_np
    assert random.random() == expected_py


def test_unseeded_runs_still_vary(labels):
    y_true, y_pred = labels
    bounds = {
        (
            bootstrap_accuracy(y_true, y_pred, n_bootstrap=200)["ci_lower"],
            bootstrap_accuracy(y_true, y_pred, n_bootstrap=200)["ci_upper"],
        )
        for _ in range(3)
    }

    assert len(bounds) > 1


def test_empty_input_returns_zeros():
    result = bootstrap_metric([], [], compute_accuracy, n_bootstrap=10, seed=1)

    assert result == {
        "metric_value": 0.0,
        "ci_lower": 0.0,
        "ci_upper": 0.0,
        "confidence": 0.95,
    }


def test_perfect_predictions_give_degenerate_ci():
    y = np.array([0, 1] * 50)
    result = bootstrap_accuracy(y, y, n_bootstrap=100, seed=3)

    assert result["metric_value"] == 1.0
    assert result["ci_lower"] == 1.0
    assert result["ci_upper"] == 1.0


def test_confidence_level_widens_interval(labels):
    y_true, y_pred = labels
    narrow = bootstrap_accuracy(y_true, y_pred, n_bootstrap=400, confidence=0.80, seed=5)
    wide = bootstrap_accuracy(y_true, y_pred, n_bootstrap=400, confidence=0.99, seed=5)

    assert wide["ci_upper"] - wide["ci_lower"] > narrow["ci_upper"] - narrow["ci_lower"]


def test_bootstrap_f1(labels):
    y_true, y_pred = labels
    result = bootstrap_f1(y_true, y_pred, n_bootstrap=100, seed=2)

    assert 0.0 <= result["ci_lower"] <= result["ci_upper"] <= 1.0


def test_bootstrap_roc_auc_separates_classes():
    rng = np.random.default_rng(11)
    y_true = np.array([0] * 100 + [1] * 100)
    y_scores = np.concatenate([rng.normal(0, 1, 100), rng.normal(3, 1, 100)])

    result = bootstrap_roc_auc(y_true, y_scores, n_bootstrap=200, seed=4)

    assert result["metric_value"] > 0.9
    assert result["ci_lower"] <= result["metric_value"] <= result["ci_upper"]


def test_bootstrap_metrics_covers_every_metric(labels):
    y_true, y_pred = labels
    results = bootstrap_metrics(
        y_true,
        y_pred,
        {"accuracy": compute_accuracy, "inverse": lambda a, b: 1 - compute_accuracy(a, b)},
        n_bootstrap=100,
        seed=6,
    )

    assert set(results) == {"accuracy", "inverse"}
    for value in results.values():
        assert value["ci_lower"] <= value["metric_value"] <= value["ci_upper"]
