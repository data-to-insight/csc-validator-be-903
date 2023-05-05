def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "555", "666", "777"],
            "DECOM": [
                "01/01/2020",
                "01/02/2020",
                "02/03/2020",
                "15/03/2010",
                "15/03/2004",
                "14/03/2014",
                pd.NA,
            ],
            "DEC": [
                "22/01/2020",
                "23/02/2020",
                "24/03/2020",
                "06/04/2010",
                "05/04/2004",
                "04/04/2014",
                pd.NA,
            ],
            "PLACE": ["T3", "T3", "T3", "T3", "T3", "P2", "T3"],
        }
    )
    fake_hea = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "555", "666"],
            "DOB": [
                "01/01/1998",
                "01/02/2000",
                "02/03/2015",
                "15/01/2010",
                "15/03/2000",
                "15/03/2000",
            ],
        }
    )
    fake_dfs = {"Episodes": fake_epi, "Header": fake_hea}

    error_defn, error_func = validate()

    assert error_func(fake_dfs) == {"Episodes": [1, 2, 3]}
