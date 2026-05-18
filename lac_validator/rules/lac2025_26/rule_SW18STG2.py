import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW18STG2",
    message="The end date of the social worker episode is before the start date",
    affected_fields=["SW_DEC", "SW_DECOM"],
    tables=["SWEpisodes"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        SWE = dfs["SWEpisodes"]
        SWE["index"] = SWE.index

        # Where provided, <SW_DEC> must be > <SW_DECOM>

        SWE["SW_DECOM"] = pd.to_datetime(
            SWE["SW_DECOM"], dayfirst=True, errors="coerce"
        )

        SWE["SW_DEC"] = pd.to_datetime(SWE["SW_DEC"], dayfirst=True, errors="coerce")

        has_dec_decom = SWE[SWE["SW_DEC"].notna() & SWE["SW_DECOM"].notna()]

        error_rows = has_dec_decom[
            ~(has_dec_decom["SW_DEC"] > has_dec_decom["SW_DECOM"])
        ].index

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
                "SW_DECOM": "02/01/2002",
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
