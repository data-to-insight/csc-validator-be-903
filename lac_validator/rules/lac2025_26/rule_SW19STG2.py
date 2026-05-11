import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW19STG2",
    message="There are 2 social worker episodes for the child starting on the same date.",
    affected_fields=["SW_DEC", "SW_DECOM"],
    tables=["SWEpisodes"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        SWE = dfs["SWEpisodes"]
        SWE["index"] = SWE.index

        # <SW_DECOM> of current social worker episode must be distinct from any other social worker episodes for this child

        SWE["DUPLICATE_DECOM"] = SWE.duplicated(["CHILD", "SW_DECOM"])

        error_rows = SWE[SWE["DUPLICATE_DECOM"] == True].index

        return {"SWEpisodes": error_rows.tolist()}


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
                "SW_DECOM": "01/01/2001",
                "SW_DEC": "01/01/2001",
            },  # 1 pass,
            {
                "CHILD": "child2",
                "SW_DECOM": "02/01/2000",
                "SW_DEC": "01/01/2001",
            },  # 2 Pass,
            {
                "CHILD": "child1",
                "SW_DECOM": "01/01/2001",
                "SW_DEC": "01/01/2001",
            },  # 3 fail,
        ]
    )

    fake_dfs = {"SWEpisodes": fake_SWE}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [3]}
