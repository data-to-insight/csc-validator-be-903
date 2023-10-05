import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="426",
    message="A child receiving respite care cannot be recorded under a legal status of V3 and V4 in "
    + "the same year.",
    affected_fields=["LS"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        epi_v3 = epi[epi["LS"] == "V3"]
        epi_v4 = epi[epi["LS"] == "V4"]

        m_coh = epi_v3.merge(epi_v4, on="CHILD", how="inner")
        err_child = m_coh["CHILD"].unique().tolist()

        err_l1 = epi_v3[epi_v3["CHILD"].isin(err_child)].index.tolist()
        err_l2 = epi_v4[epi_v4["CHILD"].isin(err_child)].index.tolist()

        err_list = err_l1 + err_l2
        err_list.sort()
        return {"Episodes": err_list}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"CHILD": "111", "LS": "V3"},  # 0
            {"CHILD": "111", "LS": "V3"},  # 1
            {"CHILD": "222", "LS": "V3"},  # 2 Fail
            {"CHILD": "222", "LS": "V4"},  # 3 Fail
            {"CHILD": "222", "LS": "X1"},  # 4
            {"CHILD": "444", "LS": "V3"},  # 5
            {"CHILD": "555", "LS": "V4"},  # 6 Fail
            {"CHILD": "555", "LS": "V3"},  # 7 Fail
            {"CHILD": "555", "LS": "V3"},  # 8 Fail
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [2, 3, 6, 7, 8]}


# EPI is an undocumented rule in the DFE portal. It checks whether each Child ID in the Header file exists in either the Episodes or OC3 file.

# Testing rule with only Header and Episodes provided.  Rule will also function with only Header provided as per DFE portal.
