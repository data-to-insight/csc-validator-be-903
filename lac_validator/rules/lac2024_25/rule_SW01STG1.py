import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW01STG1",
    message="Child looked after on 31 March, but no social worker episode information is reported",
    affected_fields=["DEC"],
)
def validate(dfs):
    if ("SWEpisodes" not in dfs) | ("Episodes" not in dfs):
        return {}
    else:
        SWE = dfs["SWEpisodes"]
        episodes = dfs["Episodes"]

        # If <CLA_AT_31_MARCH> then at least one instance of each of the following items should be provided:
        # <SW_ID>, <SW_DECOM>, <SW_REASON>

        episodes["index"] = episodes.index

        # DfE states children are <CLA_AT_31_MARCH> when
        # <DEC> of the current episode is null and <LS> not = ‘V3’, ‘V4’
        looked_after_31_mar = episodes[
            (episodes["DEC"].isna()) & ~(episodes["LS"].isin(["V3", "V4"]))
        ]

        merged_df = looked_after_31_mar.merge(SWE, on="CHILD", how="left")

        condition = merged_df["SW_ID"].isna() | merged_df["SW_DECOM"].isna()

        errors = merged_df[condition]
        error_rows = errors["index"].tolist()

        return {"SWEpisodes": error_rows}


def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        [
            {"CHILD": "child1", "DEC": pd.NA, "LS": "xx"},
            {"CHILD": "child2", "DEC": pd.NA, "LS": "xx"},
            {"CHILD": "child3", "DEC": pd.NA, "LS": "xx"},
            {"CHILD": "child4", "DEC": pd.NA, "LS": "xx"},
            {"CHILD": "child5", "DEC": "01/01/2000", "LS": "xx"},
            {"CHILD": "child6", "DEC": pd.NA, "LS": "V4"},
            {"CHILD": "child8", "DEC": pd.NA, "LS": "xx"},
            {"CHILD": "child9", "DEC": pd.NA, "LS": "xx"},
        ]
    )

    fake_swe = pd.DataFrame(
        [
            {"CHILD": "child1", "SW_ID": pd.NA, "SW_DECOM": "xx", "xx": "xx"},
            {"CHILD": "child2", "SW_ID": "xx", "SW_DECOM": pd.NA, "xx": "xx"},
            {"CHILD": "child3", "SW_ID": "xx", "SW_DECOM": "xx", "xx": pd.NA},
            {"CHILD": "child4", "SW_ID": "xx", "SW_DECOM": "xx", "xx": "xx"},
            {"CHILD": "child5", "SW_ID": "xx", "SW_DECOM": "xx", "xx": pd.NA},
            {"CHILD": "child6", "SW_ID": "xx", "SW_DECOM": "xx", "xx": pd.NA},
            {"CHILD": "child7", "SW_ID": "xx", "SW_DECOM": "xx", "SW_REASON": pd.NA},
            {"CHILD": "child9", "SW_ID": "xx", "xx": "xx", "SW_REASON": pd.NA},
        ]
    )

    fake_dfs = {"SWEpisodes": fake_swe, "Episodes": fake_epi}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [0, 1, 6, 7]}
