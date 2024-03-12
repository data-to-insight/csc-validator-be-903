import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW04STG1",
    message="Date social worker episode began is not a valid date..",
    affected_fields=["SW_DECOM"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        import lac_validator.rules.rule_utils

        df = dfs["SWEpisodes"]

        df["SW_DECOM_dt"] = df["SW_DECOM"].apply(
            lac_validator.rules.rule_utils.valid_date
        )

        error_rows = df[(df["SW_DECOM_dt"].isna()) & (~df["SW_DECOM"].isna())].index

        return {"SWEpisodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SW_DECOM": ["ZZ/ZZ/ZZZZ", "01/01/2001", "zz", "01/01/ZZZZ", pd.NA],
        }
    )

    fake_dfs = {"SWEpisodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [2]}
