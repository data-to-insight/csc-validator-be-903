import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW05STG1",
    message="Date social worker episode began is not a valid date.",
    affected_fields=["SW_DEC"],
    tables=["SWEpisodes"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:

        df = dfs["SWEpisodes"]
        
        df["SW_DEC_dt"] = pd.to_datetime(
            df["SW_DEC"], format="%d/%m/%Y", errors="coerce"
        )

        error_rows = df[(df["SW_DEC_dt"].isna()) | (df["SW_DEC"].isna())].index

        return {"SWEpisodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SW_DEC": [
                "ZZ/ZZ/ZZZZ",
                "01/01/2001",
                "zz",
                "01/01/ZZZZ",
                pd.NA,
                "1999/12/01",
            ]
        }
    )

    fake_dfs = {"SWEpisodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [0, 2, 3, 4, 5]}
