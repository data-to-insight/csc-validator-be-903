import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="501",
    message="A new episode has started before the end date of the previous episode.",
    affected_fields=["DECOM", "DEC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        epi = epi.reset_index()
        epi["DECOM"] = pd.to_datetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        epi["DEC"] = pd.to_datetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")

        epi = epi.sort_values(["CHILD", "DECOM"])

        epi_lead = epi.shift(1)
        epi_lead = epi_lead.reset_index()

        m_epi = epi.merge(
            epi_lead, left_on="index", right_on="level_0", suffixes=("", "_prev")
        )

        error_cohort = m_epi[
            (m_epi["CHILD"] == m_epi["CHILD_prev"])
            & (m_epi["DECOM"] < m_epi["DEC_prev"])
        ]
        error_list = error_cohort["index"].to_list()
        error_list.sort()
        return {"Episodes": error_list}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"CHILD": "111", "DECOM": "01/06/2020", "DEC": "04/06/2020"},  # 0
            {"CHILD": "111", "DECOM": "02/06/2020", "DEC": "06/06/2020"},  # 1   Fails
            {"CHILD": "111", "DECOM": "06/06/2020", "DEC": pd.NA},  # 2
            {"CHILD": "111", "DECOM": "08/06/2020", "DEC": "09/06/2020"},  # 3
            {"CHILD": "222", "DECOM": "10/06/2020", "DEC": "11/06/2020"},  # 4
            {"CHILD": "333", "DECOM": "04/06/2020", "DEC": "07/06/2020"},  # 5
            {"CHILD": "333", "DECOM": "05/06/2020", "DEC": pd.NA},  # 6   Fails
            {"CHILD": "444", "DECOM": "08/06/2020", "DEC": "09/06/2020"},  # 7
            {"CHILD": "444", "DECOM": "08/06/2020", "DEC": "10/06/2020"},  # 8   Fails
            {"CHILD": "444", "DECOM": "15/06/2020", "DEC": pd.NA},  # 9
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1, 6, 8]}
