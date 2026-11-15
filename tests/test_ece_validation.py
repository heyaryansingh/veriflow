import pytest
from veriflow.evaluation.metrics import compute_calibration_ece


@pytest.mark.parametrize("y_true,y_probs,n_bins", [
    ([0, 1], [0.1, 0.9], 0),
    ([0, 1, 1], [0.1, 0.9], 10),
    ([0, 1], [0.1, float("nan")], 10),
])
def test_ece_rejects_bad_input(y_true, y_probs, n_bins):
    with pytest.raises(ValueError):
        compute_calibration_ece(y_true, y_probs, n_bins=n_bins)
