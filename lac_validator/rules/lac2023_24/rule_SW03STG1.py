import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW03STG1",
    message="For each social worker episode, information should be complete.",
    affected_fields=["SW_ID", "SW_DECOM", "SW_REASON"],
    tables=["SWEpisodes"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        SWE = dfs["SWEpisodes"]

        error_df = SWE[
            SWE["SW_ID"].isna() | SWE["SW_DECOM"].isna() | SWE["SW_REASON"].isna()
        ]

        error_rows = error_df.index

        return {"SWEpisodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_swe = pd.DataFrame(
        [
            {
                "CHILD": "child1",
                "SW_ID": pd.NA,
                "SW_DECOM": "xx",
                "SW_DEC": "XX",
                "SW_REASON": "xx",
            },
            {
                "CHILD": "child2",
                "SW_ID": "xx",
                "SW_DECOM": pd.NA,
                "SW_DEC": "XX",
                "SW_REASON": "xx",
            },
            {
                "CHILD": "child3",
                "SW_ID": "xx",
                "SW_DECOM": "xx",
                "SW_DEC": "XX",
                "SW_REASON": pd.NA,
            },
            {
                "CHILD": "child4",
                "SW_ID": "xx",
                "SW_DECOM": "xx",
                "SW_DEC": pd.NA,
                "SW_REASON": "xx",
            },
            {
                "CHILD": "child5",
                "SW_ID": "xx",
                "SW_DECOM": "xx",
                "SW_DEC": "XX",
                "SW_REASON": "xx",
            },
        ]
    )

    fake_dfs = {"SWEpisodes": fake_swe}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [0, 1, 2]}
