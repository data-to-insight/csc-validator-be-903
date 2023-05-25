import pandas as pd
from lac_validator.rule_engine import rule_definition


def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "01/06/2020",
                "RNE": "L",
            },  # 0  Min, Fails
            {"CHILD": "111", "DEC": pd.NA, "DECOM": "05/06/2020", "RNE": "L"},  # 1
            {"CHILD": "111", "DEC": pd.NA, "DECOM": "06/06/2020", "RNE": "L"},  # 2
            {
                "CHILD": "123",
                "DEC": pd.NA,
                "DECOM": "08/06/2020",
                "RNE": "L",
            },  # 3  Min, Fails
            {"CHILD": "222", "DEC": pd.NA, "DECOM": "05/06/2020", "RNE": "L"},  # 4  Min
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "RNE": "L",
            },  # 5  Min, Fails
            {"CHILD": "333", "DEC": pd.NA, "DECOM": "07/06/2020", "RNE": "L"},  # 6
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "08/06/2020", "RNE": "L"},  # 7  Min
        ]
    )

    fake_epi_last = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "01/06/2020",
                "RNE": "S",
            },  # Max Different RNE
            {
                "CHILD": "123",
                "DEC": pd.NA,
                "DECOM": "08/06/2020",
                "RNE": "P",
            },  # Max Different RNE
            {
                "CHILD": "222",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "RNE": "L",
            },  # Max Same
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "RNE": "R",
            },  # Max Different RNE
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "08/06/2020", "RNE": "L"},
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "09/06/2020", "RNE": "L"},
            {
                "CHILD": "444",
                "DEC": pd.NA,
                "DECOM": "19/06/2020",
                "RNE": "L",
            },  # Max different date so passes
        ]
    )

    fake_dfs = {"Episodes": fake_epi, "Episodes_last": fake_epi_last}

    

    result = validate(fake_dfs)

    assert result == {"Episodes": [0, 3, 5]}
