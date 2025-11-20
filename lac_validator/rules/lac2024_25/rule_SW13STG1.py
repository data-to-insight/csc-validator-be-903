import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW13STG1",
    message="The reason for social worker change is not valid.",
    affected_fields=["SW_REASON"],
    tables=["SWEpisodes"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        df = dfs["SWEpisodes"]
        df = df.reset_index()

        df["SW_DECOM"] = pd.to_datetime(df["SW_DECOM"], dayfirst=True)

        valid_reasons = [
            "MANAGE",
            "FCONTA",
            "LEFTRL",
            "ORGRST",
            "TSPROC",
            "ABSENC",
            "CHCHAN",
            "PCCHAN",
            "SWDIED",
            "OTHERS",
        ]

        no_reason = df[df["SW_REASON"].isna()]
        yes_reason = df[df["SW_REASON"].notna()]

        invalid_reason = yes_reason[~yes_reason["SW_REASON"].isin(valid_reasons)]
        not_present_wrong_date = no_reason[
            no_reason["SW_DECOM"] >= pd.to_datetime("01/04/2023", dayfirst=True)
        ]

        error_df = pd.concat([not_present_wrong_date, invalid_reason])

        error_rows = error_df["index"]

        return {"SWEpisodes": sorted(error_rows.tolist())}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SW_REASON": ["LAZINESS", "SWDIED", "SLEEPINESS", "CHCHAN", pd.NA, pd.NA],
            "SW_DECOM": [
                "01/01/2000",
                "01/01/2000",
                "01/01/2000",
                "01/01/2000",
                "01/01/2000",
                "01/04/2023",
            ],
        }
    )

    fake_dfs = {"SWEpisodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [0, 2, 5]}
