import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW16bSTG2",
    message="The social worker episode start date does not match the open episode at the end of last year.",
    affected_fields=["SW_DECOM"],
)
def validate(dfs):
    if ("SWEpisodes" not in dfs) & ("SWEpisodes_last" not in dfs):
        return {}
    else:
        SWE = dfs["SWEpisodes"]
        SWE_prev = dfs["SWEpisodes_last"]

        # If present, where there is a previous collection year’s final social worker episode,
        # and <SW_DEC> not provided,
        # then first social worker episode of this year’s collection <SW_DECOM> be the same as the previous episode

        SWE_prev["SW_DECOM"] = pd.to_datetime(
            SWE_prev["SW_DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        prev_ordered = SWE_prev.sort_values(by=["SW_DECOM"], ascending=False)
        prev_ordered = prev_ordered.drop_duplicates(["CHILD"], keep="first")

        SWE["SW_DECOM"] = pd.to_datetime(
            SWE["SW_DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        current_ordered = SWE.sort_values(by=["SW_DECOM"], ascending=True)
        current_ordered = current_ordered.drop_duplicates(["CHILD"], keep="first")
        current_ordered["index"] = current_ordered.index

        no_prev_dec = prev_ordered[(prev_ordered["SW_DEC"].isna())]

        merged_df = no_prev_dec.merge(
            current_ordered, on="CHILD", how="left", suffixes=("_current", "_prev")
        )

        error_merged = merged_df[
            merged_df["SW_DECOM_current"] != merged_df["SW_DECOM_prev"]
        ]

        error_rows = SWE[SWE.index.isin(error_merged["index"])].index

        return {"SWEpisodes": error_rows.tolist()}


def test_validate():
    import pandas as pd

    fake_SWE_last = pd.DataFrame(
        [
            {
                "CHILD": "child1",
                "SW_DECOM": "01/01/2000",
                "SW_DEC": pd.NA,
                "SW_REASON": "OTHERS",
            },
            {
                "CHILD": "child1",
                "SW_DECOM": "02/01/2000",
                "SW_DEC": "01/01/2001",
                "SW_REASON": "OTHERS",
            },
            {
                "CHILD": "child2",
                "SW_DECOM": "01/01/2001",
                "SW_DEC": pd.NA,
                "SW_REASON": "OTHERS",
            },
            {
                "CHILD": "child3",
                "SW_DECOM": "01/01/2001",
                "SW_DEC": pd.NA,
                "SW_REASON": "OTHERS",
            },
            {
                "CHILD": "child4",
                "SW_DECOM": "01/01/2001",
                "SW_DEC": pd.NA,
                "SW_REASON": "OTHERS",
            },
        ]
    )

    fake_SWE = pd.DataFrame(
        [
            {
                "CHILD": "child1",
                "SW_DECOM": pd.NA,
                "SW_DEC": "01/01/2001",
                "SW_REASON": "OTHERS",
            },  # 0 pass, most recent prev has dec
            {
                "CHILD": "child2",
                "SW_DECOM": "01/01/2001",
                "SW_DEC": pd.NA,
                "SW_REASON": "OTHERS",
            },  # 1, pass, matching decom
            {
                "CHILD": "child3",
                "SW_DECOM": "02/01/2001",
                "SW_DEC": "03/01/2001",
                "SW_REASON": "FCONTA",
            },  # 2, fail, decom different
            {
                "CHILD": "child3",
                "SW_DECOM": "02/01/2001",
                "SW_DEC": pd.NA,
                "SW_REASON": "FCONTA",
            },  # 3, pass, not first episode in year
            {
                "CHILD": "child4",
                "SW_DECOM": "01/01/2001",
                "SW_DEC": "04/01/2001",
                "SW_REASON": "OTHERS",
            },  # 4 pass same decom
        ]
    )

    fake_dfs = {"SWEpisodes": fake_SWE, "SWEpisodes_last": fake_SWE_last}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [2]}
