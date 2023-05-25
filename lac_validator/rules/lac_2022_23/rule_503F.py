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
                "URN": "SC055123",
            },  # 0  Fails
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "URN": "SC055123",
            },  # 1
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "URN": "SC055123",
            },  # 2
            {
                "CHILD": "123",
                "DEC": pd.NA,
                "DECOM": "08/06/2020",
                "URN": "SC055123",
            },  # 3
            {
                "CHILD": "222",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "URN": "SC055123",
            },  # 4
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "URN": "SC055123",
            },  # 5  Fails
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "07/06/2020",
                "URN": "SC055123",
            },  # 6
            {
                "CHILD": "444",
                "DEC": pd.NA,
                "DECOM": "07/06/2020",
                "URN": "SC055123",
            },  # 7
        ]
    )

    fake_epi_last = pd.DataFrame(
        [
            {"CHILD": "111", "DEC": pd.NA, "DECOM": "01/06/2020", "URN": pd.NA},  # Max
            {
                "CHILD": "123",
                "DEC": pd.NA,
                "DECOM": "08/06/2020",
                "URN": "SC055123",
            },  # Max
            {"CHILD": "222", "DEC": pd.NA, "DECOM": "05/06/2020", "URN": "XXX"},  # Max
            {"CHILD": "333", "DEC": pd.NA, "DECOM": "06/06/2020", "URN": pd.NA},  # Max
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "08/06/2020", "URN": "XXX"},
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "09/06/2020", "URN": "SC055123"},
            {
                "CHILD": "444",
                "DEC": pd.NA,
                "DECOM": "19/06/2020",
                "URN": "SC055123",
            },  # Max
        ]
    )

    fake_dfs = {"Episodes": fake_epi, "Episodes_last": fake_epi_last}

    

    result = validate(fake_dfs)

    assert result == {"Episodes": [0, 4, 5]}
