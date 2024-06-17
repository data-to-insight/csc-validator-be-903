import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="225",
    message="Reason for placement change must be recorded.",
    affected_fields=["REASON_PLACE_CHANGE"],
    tables=["Episodes"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        epi["DECOM"] = pd.to_datetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        epi.sort_values(["CHILD", "DECOM"], inplace=True)
        epi.reset_index(inplace=True)
        epi.reset_index(inplace=True)
        epi["LAG_INDEX"] = epi["level_0"].shift(1)
        m_epi = epi.merge(
            epi,
            how="inner",
            left_on="level_0",
            right_on="LAG_INDEX",
            suffixes=["", "_NEXT"],
        )
        m_epi = m_epi[m_epi["CHILD"] == m_epi["CHILD_NEXT"]]

        mask_is_X1 = m_epi["REC"] == "X1"
        mask_null_place_chg = m_epi["REASON_PLACE_CHANGE"].isna()
        mask_place_not_T = ~m_epi["PLACE"].isin(["T0", "T1", "T2", "T3", "T4"])
        mask_next_is_PBTU = m_epi["RNE_NEXT"].isin(["P", "B", "T", "U"])
        mask_next_place_not_T = ~m_epi["PLACE_NEXT"].isin(
            ["T0", "T1", "T2", "T3", "T4"]
        )

        error_mask = (
            mask_is_X1
            & mask_null_place_chg
            & mask_place_not_T
            & mask_next_is_PBTU
            & mask_next_place_not_T
        )

        error_list = m_epi["index"][error_mask].to_list()
        return {"Episodes": error_list}


def test_validate():
    import pandas as pd

    fake_data_epi = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DECOM": "01/06/2020",
                "RNE": "P",
                "REC": "X1",
                "PLACE": "U1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 0 Fails
            {
                "CHILD": "111",
                "DECOM": "05/06/2020",
                "RNE": "P",
                "REC": "E11",
                "PLACE": "X1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 1
            {
                "CHILD": "111",
                "DECOM": "06/06/2020",
                "RNE": "B",
                "REC": "E3",
                "PLACE": "X1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 2
            {
                "CHILD": "123",
                "DECOM": "08/06/2020",
                "RNE": "P",
                "REC": "X1",
                "PLACE": "U1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 3 Fails
            {
                "CHILD": "123",
                "DECOM": "10/06/2020",
                "RNE": "P",
                "REC": "E3",
                "PLACE": "X1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 4
            {
                "CHILD": "333",
                "DECOM": "06/06/2020",
                "RNE": "T",
                "REC": "X1",
                "PLACE": "U1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 5
            {
                "CHILD": "333",
                "DECOM": "07/06/2020",
                "RNE": "L",
                "REC": "X1",
                "PLACE": "X1",
                "REASON_PLACE_CHANGE": "CHANGE",
            },  # 6 Passes as RPC not null
            {
                "CHILD": "333",
                "DECOM": "08/06/2020",
                "RNE": "P",
                "REC": "E3",
                "PLACE": "U1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 7
            {
                "CHILD": "444",
                "DECOM": "09/06/2020",
                "RNE": "U",
                "REC": "X1",
                "PLACE": "T1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 8
            {
                "CHILD": "444",
                "DECOM": "15/06/2020",
                "RNE": "P",
                "REC": "X1",
                "PLACE": "X1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 9 Passes next place T3
            {
                "CHILD": "444",
                "DECOM": "16/06/2020",
                "RNE": "P",
                "REC": "E3",
                "PLACE": "T3",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 10
            {
                "CHILD": "666",
                "DECOM": "17/06/2020",
                "RNE": "P",
                "REC": pd.NA,
                "PLACE": "T4",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 11
        ]
    )

    fake_dfs = {"Episodes": fake_data_epi}

    result = validate(fake_dfs)

    assert result == {"Episodes": [0, 3]}
