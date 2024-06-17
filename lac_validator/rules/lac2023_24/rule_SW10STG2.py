import pandas as pd
import numpy as np

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="SW10STG2",
    message="A new social worker episode has started before the end date of the previous social worker episode.",
    affected_fields=["SW_DECOM"],
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

        # <SW_DECOM> of current episode must be = (<SW_DEC>+/- 7 days) of previous episode if present.
        # Can be interpreted as meaning >= sw_dec - 7 days (which includes all days inside the tolerance)
        error_cohort = m_df[
            (~(m_df["SW_DECOM"] >= (m_df["SW_DEC_prev"] - np.timedelta64(7, "D"))))
            | (~(m_df["SW_DECOM"] <= (m_df["SW_DEC_prev"] + np.timedelta64(7, "D"))))
        ]
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
            },  # 0 Ignore no previous SW episode
            {
                "CHILD": "1",
                "SW_DECOM": "02/01/2000",
                "SW_DEC": "03/01/2000",
            },  # 1 Pass >= previous SW_DEC (-7)
            {
                "CHILD": "2",
                "SW_DECOM": "01/01/1999",
                "SW_DEC": "09/01/2000",
            },  # 2 Ignore no previous SW episode
            {
                "CHILD": "2",
                "SW_DECOM": "01/01/2000",
                "SW_DEC": "10/01/2000",
            },  # 3 Fail not >= previous SW_DEC (-7)
            {
                "CHILD": "3",
                "SW_DECOM": "10/01/2000",
                "SW_DEC": "20/01/2000",
            },  # 4 Pass (technically) same as previous SW_DEC
            {
                "CHILD": "3",
                "SW_DECOM": "10/01/2000",
                "SW_DEC": "11/01/2000",
            },  # 5 Pass (technically) same as previous SW_DEC
            {
                "CHILD": "3",
                "SW_DECOM": "18/01/2000",
                "SW_DEC": "20/01/2000",
            },  # 6 Pass <= previous SW_DEC (+7) (accounting for SW_DEC in sort)
            {
                "CHILD": "3",
                "SW_DECOM": "30/01/2000",
                "SW_DEC": "31/01/2000",
            },  # 7 Fail >= previous SW_DEC (+7) (accounting for SW_DEC in sort)
        ]
    )

    fake_dfs = {"SWEpisodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"SWEpisodes": [3, 7]}
