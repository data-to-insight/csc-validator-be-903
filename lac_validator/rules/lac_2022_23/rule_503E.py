def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "01/06/2020",
                "PLACE_PROVIDER": "PR1",
            },  # 0  Fails
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "PLACE_PROVIDER": "PR2",
            },  # 1
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "PLACE_PROVIDER": "PR3",
            },  # 2
            {
                "CHILD": "123",
                "DEC": pd.NA,
                "DECOM": "08/06/2020",
                "PLACE_PROVIDER": "PR4",
            },  # 3
            {
                "CHILD": "222",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "PLACE_PROVIDER": "PR5",
            },  # 4  Fails
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "PLACE_PROVIDER": "PR0",
            },  # 5  Fails
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "07/06/2020",
                "PLACE_PROVIDER": "PR1",
            },  # 6
            {
                "CHILD": "444",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "PLACE_PROVIDER": "PR3",
            },  # 7
        ]
    )

    fake_epi_last = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DEC": pd.NA,
                "DECOM": "01/06/2020",
                "PLACE_PROVIDER": pd.NA,
            },  # Max
            {
                "CHILD": "123",
                "DEC": pd.NA,
                "DECOM": "08/06/2020",
                "PLACE_PROVIDER": "PR4",
            },  # Max
            {
                "CHILD": "222",
                "DEC": pd.NA,
                "DECOM": "05/06/2020",
                "PLACE_PROVIDER": "PR2",
            },  # Max
            {
                "CHILD": "333",
                "DEC": pd.NA,
                "DECOM": "06/06/2020",
                "PLACE_PROVIDER": pd.NA,
            },  # Max
            {
                "CHILD": "444",
                "DEC": pd.NA,
                "DECOM": "08/06/2020",
                "PLACE_PROVIDER": "PR1",
            },
            {
                "CHILD": "444",
                "DEC": pd.NA,
                "DECOM": "09/06/2020",
                "PLACE_PROVIDER": "PR0",
            },
            {
                "CHILD": "444",
                "DEC": pd.NA,
                "DECOM": "19/06/2020",
                "PLACE_PROVIDER": "PR2",
            },  # Max
        ]
    )

    fake_dfs = {"Episodes": fake_epi, "Episodes_last": fake_epi_last}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 4, 5, 7]}
