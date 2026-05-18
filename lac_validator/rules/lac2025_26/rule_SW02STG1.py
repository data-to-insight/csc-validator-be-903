import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW02STG1",
    message="Social worker ID does not begin with the characters ‘SW’ or ‘XX’.",
    affected_fields=["SW_ID"],
    tables=["SWEpisodes"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        df = dfs["SWEpisodes"]

        error_rows = df[
            ~df["SW_ID"].str[:2].isin(["SW", "XX"]) | (df["SW_ID"].str.len() < 4)
        ].index

        return {"SWEpisodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SW_ID": [
                "SW000",
                "XX000",
                "aa00",  # FAILS
                "xx000",  # FAILS
                "SW",  # FAILS
                "XX",
            ],  # FAILS
        }
    )

    fake_dfs = {"SWEpisodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [2, 3, 4, 5]}
