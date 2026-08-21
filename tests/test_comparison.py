"""Tests for baseline comparison, focused on metric direction.

A regression gate that treats every metric as higher-is-better will pass a run
whose calibration error tripled and fail one that fixed it, so the direction of
each metric is what these tests pin down.
"""

from datetime import datetime

from veriflow.evaluation.comparison import (
    compare_results,
    compute_metric_delta,
    is_lower_better,
    is_significant_change,
)
from veriflow.evaluation.results import EvaluationResult


def _result(metrics, cis=None):
    return EvaluationResult(
        metrics=metrics,
        bootstrap_cis=cis or {},
        metadata={"n_samples": 100},
        timestamp=datetime(2024, 1, 1),
    )


def _ci(lower, upper):
    return {"ci_lower": lower, "ci_upper": upper, "confidence": 0.95}


class TestIsLowerBetter:
    def test_error_style_metrics(self):
        for name in [
            "calibration_ece",
            "ece",
            "brier_score",
            "log_loss",
            "val_loss",
            "mae",
            "rmse",
            "error_rate",
        ]:
            assert is_lower_better(name), name

    def test_score_style_metrics(self):
        for name in ["accuracy", "f1", "roc_auc", "precision", "recall"]:
            assert not is_lower_better(name), name

    def test_is_case_insensitive(self):
        assert is_lower_better("Calibration_ECE")


class TestComputeMetricDelta:
    def test_higher_is_better_by_default(self):
        assert compute_metric_delta(0.9, 0.8)["improved"] is True
        assert compute_metric_delta(0.7, 0.8)["improved"] is False

    def test_lower_is_better_inverts_the_verdict(self):
        assert compute_metric_delta(0.02, 0.10, lower_is_better=True)["improved"] is True
        assert compute_metric_delta(0.10, 0.02, lower_is_better=True)["improved"] is False

    def test_relative_change_is_signed(self):
        info = compute_metric_delta(0.9, 0.8)
        assert info["delta"] == compute_metric_delta(0.9, 0.8)["delta"]
        assert info["relative_change"] > 0

    def test_zero_baseline_does_not_divide(self):
        assert compute_metric_delta(0.5, 0.0)["relative_change"] == float("inf")
        assert compute_metric_delta(0.0, 0.0)["relative_change"] == 0.0


class TestCompareResults:
    def test_worse_calibration_is_a_regression(self):
        current = _result({"calibration_ece": 0.20}, {"calibration_ece": _ci(0.20, 0.20)})
        baseline = _result({"calibration_ece": 0.02}, {"calibration_ece": _ci(0.02, 0.02)})

        report = compare_results(current, baseline)

        assert report["comparisons"][0]["status"] == "regressed"
        assert report["passed"] is False

    def test_better_calibration_is_an_improvement(self):
        current = _result({"calibration_ece": 0.02}, {"calibration_ece": _ci(0.02, 0.02)})
        baseline = _result({"calibration_ece": 0.20}, {"calibration_ece": _ci(0.20, 0.20)})

        report = compare_results(current, baseline)

        assert report["comparisons"][0]["status"] == "improved"
        assert report["passed"] is True

    def test_accuracy_direction_is_unchanged(self):
        current = _result({"accuracy": 0.70}, {"accuracy": _ci(0.66, 0.74)})
        baseline = _result({"accuracy": 0.90}, {"accuracy": _ci(0.86, 0.94)})

        report = compare_results(current, baseline)

        assert report["comparisons"][0]["status"] == "regressed"
        assert report["passed"] is False

    def test_overlapping_intervals_are_not_significant(self):
        current = _result({"accuracy": 0.81}, {"accuracy": _ci(0.75, 0.87)})
        baseline = _result({"accuracy": 0.80}, {"accuracy": _ci(0.74, 0.86)})

        report = compare_results(current, baseline)

        assert report["comparisons"][0]["status"] == "unchanged"
        assert report["passed"] is True

    def test_missing_metric_fails_the_gate(self):
        current = _result({"accuracy": 0.9})
        baseline = _result({"accuracy": 0.9, "f1": 0.8})

        report = compare_results(current, baseline)

        statuses = {c["metric"]: c["status"] for c in report["comparisons"]}
        assert statuses["f1"] == "missing"
        assert report["passed"] is False

    def test_new_metric_does_not_fail_the_gate(self):
        current = _result({"accuracy": 0.9, "f1": 0.8})
        baseline = _result({"accuracy": 0.9})

        report = compare_results(current, baseline)

        statuses = {c["metric"]: c["status"] for c in report["comparisons"]}
        assert statuses["f1"] == "new"
        assert report["passed"] is True

    def test_mixed_metrics_are_judged_independently(self):
        current = _result(
            {"accuracy": 0.95, "calibration_ece": 0.30},
            {"accuracy": _ci(0.93, 0.97), "calibration_ece": _ci(0.30, 0.30)},
        )
        baseline = _result(
            {"accuracy": 0.80, "calibration_ece": 0.05},
            {"accuracy": _ci(0.76, 0.84), "calibration_ece": _ci(0.05, 0.05)},
        )

        report = compare_results(current, baseline)

        statuses = {c["metric"]: c["status"] for c in report["comparisons"]}
        assert statuses["accuracy"] == "improved"
        assert statuses["calibration_ece"] == "regressed"
        assert report["passed"] is False


class TestIsSignificantChange:
    def test_disjoint_intervals(self):
        assert is_significant_change(_ci(0.90, 0.95), _ci(0.70, 0.80)) is True

    def test_overlapping_intervals(self):
        assert is_significant_change(_ci(0.75, 0.90), _ci(0.70, 0.80)) is False
