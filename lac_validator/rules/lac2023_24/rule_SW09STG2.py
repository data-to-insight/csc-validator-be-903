import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW09STG2",
    message="Social worker episode appears to have lasted for less than 24 hours.",
    affected_fields=["SW_DECOM", "SW_DEC"],
    tables=["SWEpisodes"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        df = dfs["SWEpisodes"]

        error_rows = df[df["SW_DEC"] == df["SW_DECOM"]].index

        return {"SWEpisodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"CHILD": "1", "SW_DEC": "01/01/2000", "SW_DECOM": "01/01/2000"},  # fail
            {"CHILD": "1", "SW_DEC": "01/01/2000", "SW_DECOM": "02/01/2000"},
            {"CHILD": "2", "SW_DEC": "01/01/1901", "SW_DECOM": "01/01/1901"},  # fail
            {"CHILD": "2", "SW_DEC": "01/01/1901", "SW_DECOM": pd.NA},
            {"CHILD": "3", "SW_DEC": pd.NA, "SW_DECOM": pd.NA},
        ]
    )

    fake_dfs = {"SWEpisodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [0, 2]}
