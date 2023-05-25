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
                "CIN": "N1",
            },  # 0  Fails
            {"CHILD": "111", "DEC": pd.NA, "DECOM": "05/06/2020", "CIN": "N2"},  # 1
            {"CHILD": "111", "DEC": pd.NA, "DECOM": "06/06/2020", "CIN": "N3"},  # 2
            {"CHILD": "123", "DEC": pd.NA, "DECOM": "08/06/2020", "CIN": "N4"},  # 3
            {
                "CHILD": "222",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "CIN": "N5",
            },  # 4  Fails
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "CIN": "N6",
            },  # 5  Fails
            {"CHILD": "333", "DEC": pd.NA, "DECOM": "07/06/2020", "CIN": "N7"},  # 6
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "03/06/2020", "CIN": "N3"},  # 7
        ]
    )

    fake_epi_last = pd.DataFrame(
        [
            {"CHILD": "111", "DEC": pd.NA, "DECOM": "01/06/2020", "CIN": pd.NA},  # Max
            {"CHILD": "123", "DEC": pd.NA, "DECOM": "08/06/2020", "CIN": "N4"},  # Max
            {"CHILD": "222", "DEC": pd.NA, "DECOM": "05/06/2020", "CIN": "L"},  # Max
            {"CHILD": "333", "DEC": pd.NA, "DECOM": "06/06/2020", "CIN": pd.NA},  # Max
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "08/06/2020", "CIN": "L"},
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "09/06/2020", "CIN": "L"},
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "19/06/2020", "CIN": "L"},  # Max
        ]
    )

    fake_dfs = {"Episodes": fake_epi, "Episodes_last": fake_epi_last}

    

    result = validate(fake_dfs)

    assert result == {"Episodes": [0, 4, 5, 7]}
