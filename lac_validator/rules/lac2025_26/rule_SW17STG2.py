import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW17STG2",
    message="There is no social worker episode open at 31 March",
    affected_fields=["SW_DEC"],
    tables=["SWEpisodes"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        SWE = dfs["SWEpisodes"]
        SWE["index"] = SWE.index

        # For the last SW episode (i.e. the episode with the latest <DECOM>), <SW_DEC> must be NULL

        SWE["SW_DECOM"] = pd.to_datetime(
            SWE["SW_DECOM"], dayfirst=True, errors="coerce"
        )

        eps_sorted = SWE.sort_values(by=["SW_DECOM"], ascending=False)
        most_recent_ep = eps_sorted.drop_duplicates("CHILD", keep="first")

        print(most_recent_ep)

        most_recent_has_dec = most_recent_ep[most_recent_ep["SW_DEC"].notna()]

        error_rows = SWE[SWE.index.isin(most_recent_has_dec["index"])].index

        return {"SWEpisodes": error_rows.tolist()}
        # return {"SWEpisodes": most_recent_ep}


def test_validate():
    import pandas as pd

    fake_SWE = pd.DataFrame(
        [
            {
                "CHILD": "child1",
                "SW_DECOM": "01/01/2001",
                "SW_DEC": pd.NA,
            },  # 0 pass,
            {
                "CHILD": "child2",
                "SW_DECOM": "01/01/2000",
                "SW_DEC": "01/01/2001",
            },  # 1 pass,
            {
                "CHILD": "child2",
                "SW_DECOM": "02/01/2000",
                "SW_DEC": "01/01/2001",
            },  # 2 fail,
            {
                "CHILD": "child1",
                "SW_DECOM": "01/01/2000",
                "SW_DEC": "01/01/2001",
            },  # 0 pass,
        ]
    )

    fake_dfs = {"SWEpisodes": fake_SWE}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [2]}
