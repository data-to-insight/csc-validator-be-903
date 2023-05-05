from validator903.types import ErrorDefinition


@rule_definition(
    code="628",
    message="Motherhood details are not required for care leavers who have not been looked after during the year.",
    affected_fields=["MOTHER"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Header" not in dfs or "OC3" not in dfs:
        return {}
    else:
        hea = dfs["Header"]
        epi = dfs["Episodes"]
        oc3 = dfs["OC3"]

        hea = hea.resetindex()
        oc3nonulls = oc3[oc3[["INTOUCH", "ACTIV", "ACCOM"]].notna().any(axis=1)]

        heamergeepi = hea.merge(epi, how="left", on="CHILD", indicator=True)
        heanotinepi = heamergeepi[heamergeepi["merge"] == "leftonly"]

        cohorttocheck = heanotinepi.merge(oc3nonulls, how="inner", on="CHILD")
        errorcohort = cohorttocheck[cohorttocheck["MOTHER"].notna()]

        errorlist = list(set(errorcohort["index"].tolist()))
        errorlist.sort()
        return {"Header": errorlist}


def test_validate():
    import pandas as pd

    fake_data_hea = pd.DataFrame(
        {
            "CHILD": ["0", "1", "2", "3", "4", "5", "6"],
            "MOTHER": [1, pd.NA, 0, 1, 0, 1, 1],  # 1 will pass as null
        }
    )
    fake_data_epi = pd.DataFrame(
        {
            "CHILD": [
                "a",
                "1",
                "3",
                "3",
                "3",
                "4",
                "5",
            ],  # So 0, 2 and 6 are the ones not in episodes
        }
    )
    fake_data_oc3 = pd.DataFrame(
        [
            {"CHILD": "0", "IN_TOUCH": "Whatever", "ACTIV": pd.NA, "ACCOM": "Whatever"},
            {
                "CHILD": "2",
                "IN_TOUCH": pd.NA,
                "ACTIV": pd.NA,
                "ACCOM": pd.NA,
            },  # All null values so 2 will pass
            {"CHILD": "6", "IN_TOUCH": "Whatever", "ACTIV": pd.NA, "ACCOM": pd.NA},
            {"CHILD": "5", "IN_TOUCH": "Whatever", "ACTIV": pd.NA, "ACCOM": pd.NA},
        ]
    )
    fake_dfs = {
        "Header": fake_data_hea,
        "Episodes": fake_data_epi,
        "OC3": fake_data_oc3,
    }

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [0, 6]}
