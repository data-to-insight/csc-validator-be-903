from validator903.types import ErrorDefinition


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
        epiv3 = epi[epi["LS"] == "V3"]
        epiv4 = epi[epi["LS"] == "V4"]

        mcoh = epiv3.merge(epiv4, on="CHILD", how="inner")
        errchild = mcoh["CHILD"].unique().tolist()

        errl1 = epiv3[epiv3["CHILD"].isin(errchild)].index.tolist()
        errl2 = epiv4[epiv4["CHILD"].isin(errchild)].index.tolist()

        errlist = errl1 + errl2
        errlist.sort()
        return {"Episodes": errlist}


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

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [2, 3, 6, 7, 8]}


# EPI is an undocumented rule in the DFE portal. It checks whether each Child ID in the Header file exists in either the Episodes or OC3 file.

# Testing rule with only Header and Episodes provided.  Rule will also function with only Header provided as per DFE portal.
