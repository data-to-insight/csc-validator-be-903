import pandas as pd
from lac_validator.rule_engine import rule_definition


def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        [
            {"CHILD": "111", "DEC": pd.NA, "DECOM": "01/06/2020", "LS": "L"},  # 0  Min
            {"CHILD": "111", "DEC": pd.NA, "DECOM": "05/06/2020", "LS": "L"},  # 1
            {"CHILD": "111", "DEC": pd.NA, "DECOM": "06/06/2020", "LS": "L"},  # 2
            {
                "CHILD": "123",
                "DEC": pd.NA,
                "DECOM": "08/06/2020",
                "LS": "L",
            },  # 3  Min, Fails
            {"CHILD": "222", "DEC": pd.NA, "DECOM": "05/06/2020", "LS": "L"},  # 4  Min
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "LS": "L",
            },  # 5  Min, Fails
            {"CHILD": "333", "DEC": pd.NA, "DECOM": "07/06/2020", "LS": "L"},  # 6
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "08/06/2020", "LS": "L"},  # 7  Min
        ]
    )

    fake_epi_last = pd.DataFrame(
        [
            {"CHILD": "111", "DEC": pd.NA, "DECOM": "01/06/2020", "LS": "L"},  # Max
            {"CHILD": "123", "DEC": pd.NA, "DECOM": "08/06/2020", "LS": "E1"},  # Max
            {"CHILD": "222", "DEC": pd.NA, "DECOM": "05/06/2020", "LS": "L"},  # Max
            {"CHILD": "333", "DEC": pd.NA, "DECOM": "06/06/2020", "LS": "R"},  # Max
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "08/06/2020", "LS": "L"},
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "09/06/2020", "LS": "L"},
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "19/06/2020", "LS": "L"},  # Max
        ]
    )

    fake_dfs = {"Episodes": fake_epi, "Episodes_last": fake_epi_last}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [3, 5]}
