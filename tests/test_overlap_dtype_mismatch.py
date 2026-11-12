import pandas as pd

from veriflow.data.overlap import find_overlap


def test_overlap_detected_across_int_and_str_keys():
    a = pd.DataFrame({"id": [1, 2, 3]})
    b = pd.DataFrame({"id": ["1", "2"]})
    assert find_overlap(a, b)["overlap_count"] == 2
