def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "01/06/2020",
                "PL_LOCATION": "IN",
            },  # 0  Fails
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "PL_LOCATION": "IN",
            },  # 1
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "PL_LOCATION": "IN",
            },  # 2
            {
                "CHILD": "123",
                "DEC": pd.NA,
                "DECOM": "08/06/2020",
                "PL_LOCATION": "OUT",
            },  # 3
            {
                "CHILD": "222",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "PL_LOCATION": "IN",
            },  # 4  Fails
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "PL_LOCATION": "OUT",
            },  # 5  Fails
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "07/06/2020",
                "PL_LOCATION": "IN",
            },  # 6
            {
                "CHILD": "444",
                "DEC": pd.NA,
                "DECOM": "08/06/2020",
                "PL_LOCATION": "OUT",
            },  # 7
        ]
    )

    fake_epi_last = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "01/06/2020",
                "PL_LOCATION": pd.NA,
            },  # Max
            {
                "CHILD": "123",
                "DEC": pd.NA,
                "DECOM": "08/06/2020",
                "PL_LOCATION": "OUT",
            },  # Max
            {
                "CHILD": "222",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "PL_LOCATION": "OUT",
            },  # Max
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "PL_LOCATION": pd.NA,
            },  # Max
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "08/06/2020", "PL_LOCATION": "IN"},
            {"CHILD": "444", "DEC": pd.NA, "DECOM": "09/06/2020", "PL_LOCATION": "OUT"},
            {
                "CHILD": "444",
                "DEC": pd.NA,
                "DECOM": "19/06/2020",
                "PL_LOCATION": "OUT",
            },  # Max
        ]
    )

    fake_dfs = {"Episodes": fake_epi, "Episodes_last": fake_epi_last}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 4, 5]}
