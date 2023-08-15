import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="431",
    message="The reason for new episode is started to be looked after, but the previous episode ended on the same day.",
    affected_fields=["RNE", "DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        epi["DECOM"] = pd.to_datetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        epi["DEC"] = pd.to_datetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")
        epi.sort_values(["CHILD", "DECOM"], inplace=True)

        epi.reset_index(inplace=True)
        epi.reset_index(inplace=True)
        epi["LAG_INDEX"] = epi["level_0"].shift(-1)

        m_epi = epi.merge(
            epi,
            how="inner",
            left_on="level_0",
            right_on="LAG_INDEX",
            suffixes=["", "_PREV"],
        )

        m_epi = m_epi[(m_epi["CHILD"] == m_epi["CHILD_PREV"]) & (m_epi["RNE"] == "S")]
        error_mask = m_epi["DECOM"] <= m_epi["DEC_PREV"]
        error_list = m_epi["index"][error_mask].to_list()
        error_list.sort()
        return {"Episodes": error_list}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "RNE": "S",
                "DECOM": "01/06/2020",
                "DEC": "04/06/2020",
            },  # 0
            {
                "CHILD": "111",
                "RNE": "S",
                "DECOM": "05/06/2020",
                "DEC": "06/06/2020",
            },  # 1
            {
                "CHILD": "111",
                "RNE": "T",
                "DECOM": "06/06/2020",
                "DEC": "08/06/2020",
            },  # 2
            {
                "CHILD": "111",
                "RNE": "S",
                "DECOM": "08/06/2020",
                "DEC": "05/06/2020",
            },  # 3  Fails
            {
                "CHILD": "222",
                "RNE": "S",
                "DECOM": "05/06/2020",
                "DEC": "06/06/2020",
            },  # 4
            {
                "CHILD": "333",
                "RNE": "S",
                "DECOM": "06/06/2020",
                "DEC": "07/06/2020",
            },  # 5
            {"CHILD": "333", "RNE": "S", "DECOM": "10/06/2020", "DEC": pd.NA},  # 6
            {
                "CHILD": "444",
                "RNE": "S",
                "DECOM": "08/06/2020",
                "DEC": "09/06/2020",
            },  # 7
            {
                "CHILD": "444",
                "RNE": "S",
                "DECOM": "09/06/2020",
                "DEC": "10/06/2020",
            },  # 8  Fails
            {"CHILD": "444", "RNE": "S", "DECOM": "15/06/2020", "DEC": pd.NA},  # 9
            {
                "CHILD": "555",
                "RNE": "S",
                "DECOM": "11/06/2020",
                "DEC": "12/06/2020",
            },  # 10
            {
                "CHILD": "6666",
                "RNE": "S",
                "DECOM": "12/06/2020",
                "DEC": "13/06/2020",
            },  # 11
            {
                "CHILD": "6666",
                "RNE": "S",
                "DECOM": "13/06/2020",
                "DEC": "14/06/2020",
            },  # 12 Fails
            {
                "CHILD": "6666",
                "RNE": "S",
                "DECOM": "14/06/2020",
                "DEC": "15/06/2020",
            },  # 13 Fails
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [3, 8, 12, 13]}
