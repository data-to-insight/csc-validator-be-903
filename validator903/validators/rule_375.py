def validate():
    return validate_370to376and379("375")


def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        {
            "CHILD": ["111", "222", "333", "444", "555", "666"],
            "DECOM": [
                "01/01/2020",
                "01/02/2020",
                "02/03/2020",
                "15/03/2010",
                "15/03/2004",
                "14/03/2014",
            ],
            "DEC": [
                "13/02/2020",
                "14/03/2020",
                "14/04/2020",
                "27/04/2010",
                "26/04/2004",
                "25/04/2014",
            ],
            "PLACE": ["T1", "T1", "T1", "T1", "T1", "P2"],
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

    assert error_func(fake_dfs) == {"Episodes": [0, 2, 3]}
