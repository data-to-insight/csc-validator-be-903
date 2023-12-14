import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW03STG1",
    message="For each social worker episode, information should be complete.",
    affected_fields=["SW_ID", "SW_DECOM", "SW_DEC", "SW_REASON"],
)
def validate(dfs):
    if ("SWEpisodes" not in dfs) | ("Episodes" not in dfs):
        return {}
    else:
        SWE = dfs["SWEpisodes"]
        episodes = dfs["Episodes"]

        # DfE states children are <CLA_AT_31_MARCH> when
        # <DEC> of the current episode is null and <LS> not = ‘V3’, ‘V4’
        looked_after_31_mar = episodes[
            (episodes["DEC"].isna()) & ~(episodes["LA"].isin(["V3", "V4"]))
        ].copy()

        looked_after_31_mar["LA31M"] = "Y"
        merged_df = SWE.merge(
            looked_after_31_mar[["LA31M", "CHILD"]], on="CHILD", how="left"
        )

        error_df = merged_df[
            merged_df["SW_ID"].isna()
            | merged_df["SW_DECOM"].isna()
            | (merged_df["SW_DEC"].isna() & (merged_df["LA31M"] != "Y"))
            | merged_df["SW_REASON"].isna()
        ]

        error_rows = error_df.index

        return {"SWEpisodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_epi = pd.DataFrame(
        [
            {
                "CHILD": "child1",
                "DEC": pd.NA,
                "LA": "V3",
            },  # Fails, looked after at 31 mar and no SW ID
            {
                "CHILD": "child2",
                "DEC": pd.NA,
                "LA": "V4",
            },  # Fails, looked after at 31 mar and no SW DECOM
            {
                "CHILD": "child3",
                "DEC": pd.NA,
                "LA": "xx",
            },  # Fails, looked after at 31 mar and no SW REASON
            {
                "CHILD": "child4",
                "DEC": pd.NA,
                "LA": pd.NA,
            },  # Passes, no SW DEC, but not looked after at 31 march
            {
                "CHILD": "child6",
                "DEC": pd.NA,
                "LA": "V3",
            },  # Fails, looked after at 31 mar and no SW DEC
        ]
    )

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
            {
                "CHILD": "child6",
                "SW_ID": "xx",
                "SW_DECOM": "xx",
                "SW_DEC": pd.NA,
                "SW_REASON": "xx",
            },
        ]
    )

    fake_dfs = {"SWEpisodes": fake_swe, "Episodes": fake_epi}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [0, 1, 2, 5]}
