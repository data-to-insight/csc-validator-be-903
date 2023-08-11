import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="383",
    message="A child in a temporary placement must subsequently return to his/her normal placement.",
    affected_fields=["PLACE"],
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
        epi["LAG_INDEX"] = epi["level_0"].shift(-1)
        epi["LEAD_INDEX"] = epi["level_0"].shift(1)

        m_epi = epi.merge(
            epi,
            how="inner",
            left_on="level_0",
            right_on="LAG_INDEX",
            suffixes=["", "_TOP"],
        )
        m_epi = m_epi.merge(
            epi,
            how="inner",
            left_on="level_0",
            right_on="LEAD_INDEX",
            suffixes=["", "_BOTM"],
        )
        m_epi = m_epi[m_epi["CHILD"] == m_epi["CHILD_TOP"]]
        m_epi = m_epi[m_epi["CHILD"] == m_epi["CHILD_BOTM"]]
        m_epi = m_epi[m_epi["PLACE"].isin(["T0", "T1", "T2", "T3", "T4"])]

        mask1 = m_epi["RNE_BOTM"] != "P"
        mask2 = m_epi["PLACE_BOTM"] != m_epi["PLACE_TOP"]
        err_mask = mask1 | mask2
        err_list = m_epi["index"][err_mask].unique().tolist()
        err_list.sort()
        return {"Episodes": err_list}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"CHILD": "111", "RNE": "S", "DECOM": "01/06/2020", "PLACE": "S1"},  # 0
            {
                "CHILD": "111",
                "RNE": "S",
                "DECOM": "05/06/2020",
                "PLACE": "T1",
            },  # 1 Middle Fails as next RNE not P
            {"CHILD": "111", "RNE": "T", "DECOM": "06/06/2020", "PLACE": "S1"},  # 2
            {"CHILD": "222", "RNE": "S", "DECOM": "05/06/2020", "PLACE": "T1"},  # 3
            {"CHILD": "333", "RNE": "S", "DECOM": "06/06/2020", "PLACE": "S1"},  # 4
            {
                "CHILD": "333",
                "RNE": "S",
                "DECOM": "10/06/2020",
                "PLACE": "T1",
            },  # 5 Middle Fails as pre PL not next PL
            {"CHILD": "333", "RNE": "P", "DECOM": "12/06/2020", "PLACE": "S2"},  # 6
            {"CHILD": "444", "RNE": "S", "DECOM": "08/06/2020", "PLACE": "T1"},  # 7
            {
                "CHILD": "444",
                "RNE": "S",
                "DECOM": "09/06/2020",
                "PLACE": "P4",
            },  # 8  Middle Passes not a T code
            {"CHILD": "444", "RNE": "S", "DECOM": "15/06/2020", "PLACE": "T1"},  # 9
            {"CHILD": "6666", "RNE": "S", "DECOM": "12/06/2020", "PLACE": "T1"},  # 10
            {
                "CHILD": "6666",
                "RNE": "S",
                "DECOM": "13/06/2020",
                "PLACE": "T1",
            },  # 11 Middle Passes
            {"CHILD": "6666", "RNE": "P", "DECOM": "14/06/2020", "PLACE": "T1"},  # 12
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [1, 5]}
