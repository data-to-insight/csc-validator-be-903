from validator903.validators import *
import pandas as pd


def test_validate_101():
    fake_header = pd.DataFrame({
        'SEX': [1, 2, 3, pd.NA],
    })

    dfs = {
      'Header': fake_header,
    }

    error_def, error_func = validate_101()

    result = error_func(dfs)

    assert result == {
      'Header': [2, 3],
    }