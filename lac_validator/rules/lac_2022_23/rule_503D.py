def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "01/06/2020",
                "PLACE": "T1",
            },  # 0  Fails
            {"CHILD": "111", "DEC": pd.NA, "DECOM": "05/06/2020", "PLACE": "T2"},  # 1
            {"CHILD": "111", "DEC": pd.NA, "DECOM": "06/06/2020", "PLACE": "T3"},  # 2
            {
                "CHILD": "123",
                "DEC": pd.NA,
                "DECOM": "08/06/2020",
                "PLACE": "T4",
            },  # 3  Fails
            {
                "CHILD": "222",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "PLACE": "T5",
            },  # 4  Fails
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "PLACE": "T6",
            },  # 5  Fails
            {"CHILD": "333", "DEC": pd.NA, "DECOM": "07/06/2020", "PLACE": "T7"},  # 6
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "08/06/2020", "PLACE": "T3"},  # 7
        ]
    )

    fake_epi_last = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "01/06/2020",
                "PLACE": pd.NA,
            },  # Max
            {"CHILD": "123", "DEC": pd.NA, "DECOM": "08/06/2020", "PLACE": "N4"},  # Max
            {"CHILD": "222", "DEC": pd.NA, "DECOM": "05/06/2020", "PLACE": "L"},  # Max
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "PLACE": pd.NA,
            },  # Max
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "08/06/2020", "PLACE": "L"},
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "09/06/2020", "PLACE": "L"},
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "19/06/2020", "PLACE": "L"},  # Max
        ]
    )

    fake_dfs = {"Episodes": fake_epi, "Episodes_last": fake_epi_last}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 3, 4, 5, 7]}
