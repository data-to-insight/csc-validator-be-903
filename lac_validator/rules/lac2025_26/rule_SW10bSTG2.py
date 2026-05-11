import pandas as pd
import numpy as np

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW10bSTG2",
    message="A new social worker episode has started with a reason of first contact before the previous episode has ended.",
    affected_fields=["SW_DECOM", "SW_REASON"],
    tables=["SWEpisodes"],
)
def validate(dfs):
    if "SWEpisodes" not in dfs:
        return {}
    else:
        df = dfs["SWEpisodes"]

        df = df.reset_index()
        df["SW_DECOM"] = pd.to_datetime(
            df["SW_DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        df["SW_DEC"] = pd.to_datetime(df["SW_DEC"], format="%d/%m/%Y", errors="coerce")

        df = df.sort_values(["CHILD", "SW_DECOM", "SW_DEC"])

        df_lead = df.shift(1)
        df_lead = df_lead.reset_index()

        m_df = df.merge(
            df_lead,
            left_on=["CHILD", "index"],
            right_on=["CHILD", "level_0"],
            suffixes=("", "_prev"),
        )

        # If the current social worker episode <SW_REASON> = ‘FCONTA’ then
        # <SW_DECOM> of current episode must be > <SW_DEC> of previous episode if present.
        # Fails if FCONTA with previous SW_DEC later than SW_DECOM
        error_cohort = m_df[
            (m_df["SW_REASON"] == "FCONTA")
            & ((m_df["SW_DECOM"] <= m_df["SW_DEC_prev"]))
        ]

        print(error_cohort["SW_REASON"])
        error_list = error_cohort["index"].to_list()
        error_list.sort()

        return {"SWEpisodes": error_list}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "1",
                "SW_DECOM": "01/01/2000",
                "SW_DEC": "09/01/2000",
                "SW_REASON": "XXXX",
            },  # 0 Ignore no previous SW episode
            {
                "CHILD": "1",
                "SW_DECOM": "02/01/2000",
                "SW_DEC": "03/01/2000",
                "SW_REASON": "XXXX",
            },  # 1 Pass, not FCONTA
            {
                "CHILD": "2",
                "SW_DECOM": "01/01/1999",
                "SW_DEC": "09/01/2000",
                "SW_REASON": "XXXX",
            },  # 2 Ignore no previous SW episode
            {
                "CHILD": "2",
                "SW_DECOM": "01/01/2000",
                "SW_DEC": "10/01/2000",
                "SW_REASON": "XXXX",
            },  # 3 PASS not FCONTA
            {
                "CHILD": "3",
                "SW_DECOM": "10/01/2000",
                "SW_DEC": "20/01/2000",
                "SW_REASON": "XXXX",
            },  # 4
            {
                "CHILD": "3",
                "SW_DECOM": "10/01/2000",
                "SW_DEC": "11/01/2000",
                "SW_REASON": "XXXX",
            },  # 5
            {
                "CHILD": "3",
                "SW_DECOM": "18/01/2000",
                "SW_DEC": "20/01/2000",
                "SW_REASON": "XXXX",
            },  # 6
            {
                "CHILD": "3",
                "SW_DECOM": "19/01/2000",
                "SW_DEC": "21/01/2000",
                "SW_REASON": "FCONTA",
            },  # 7
            {
                "CHILD": "6",
                "SW_DECOM": "01/01/1999",
                "SW_DEC": "02/01/2000",
                "SW_REASON": "XXXX",
            },  # 8
            {
                "CHILD": "6",
                "SW_DECOM": "01/01/2000",
                "SW_DEC": "8/01/2000",
                "SW_REASON": "FCONTA",
            },  # 9 Fails, DECOM before previous DEC
        ]
    )

    fake_dfs = {"SWEpisodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [7, 9]}
