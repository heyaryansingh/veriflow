import numpy as np
import pandas as pd

from veriflow.data.missing_values import check_missing_values


def test_non_string_column_names_do_not_crash():
    df = pd.DataFrame({0: [np.nan, np.nan, 1], 1: [1, 2, 3]})
    r = check_missing_values(df, threshold=0.5)
    assert not r["passed"] and "0" in r["summary"]
