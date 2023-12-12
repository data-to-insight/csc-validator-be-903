import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW13STG1",
    message="The reason for social worker change is either not valid or has not been entered.",
    affected_fields=["SW_REASON"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        df = dfs["SWEpisodes"]

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

        error_rows = df[~df["SW_REASON"].isin(valid_reasons)].index

        return {"SWEpisodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SW_REASON": ["LAZINESS", "SWDIED", "SLEEPINESS", "CHCHAN"],
        }
    )

    fake_dfs = {"SWEpisodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [0, 2]}
