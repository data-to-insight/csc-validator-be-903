from validator903.types import ErrorDefinition


@rule_definition(
    code="215",
    message="Child has care leaver information but one or more data items relating to children looked after for 12 months have been completed.",
    affected_fields=[
        "IN_TOUCH",
        "ACTIV",
        "ACCOM",
        "CONVICTED",
        "HEALTH_CHECK",
        "IMMUNISATIONS",
        "TEETH_CHECK",
        "HEALTH_ASSESSMENT",
        "SUBSTANCE_MISUSE",
        "INTERVENTION_RECEIVED",
        "INTERVENTION_OFFERED",
    ],
)
def validate(dfs):
    if "OC3" not in dfs or "OC2" not in dfs:
        return {}
    else:
        oc3 = dfs["OC3"]
        oc2 = dfs["OC2"]
        # prepare to merge
        oc3.resetindex(inplace=True)
        oc2.resetindex(inplace=True)
        merged = oc3.merge(oc2, on="CHILD", how="left", suffixes=["3", "2"])
        # If any of <INTOUCH>, <ACTIV> or <ACCOM> have been provided then <CONVICTED>; <HEALTHCHECK>; <IMMUNISATIONS>; <TEETHCHECK>; <HEALTHASSESSMENT>; <SUBSTANCE MISUSE>; <INTERVENTIONRECEIVED>; <INTERVENTIONOFFERED>; should not be provided
        mask = (
            merged["INTOUCH"].notna()
            | merged["ACTIV"].notna()
            | merged["ACCOM"].notna()
        ) & (
            merged["CONVICTED"].notna()
            | merged["HEALTHCHECK"].notna()
            | merged["IMMUNISATIONS"].notna()
            | merged["TEETHCHECK"].notna()
            | merged["HEALTHASSESSMENT"].notna()
            | merged["SUBSTANCEMISUSE"].notna()
            | merged["INTERVENTIONRECEIVED"].notna()
            | merged["INTERVENTIONOFFERED"].notna()
        )

        # error locations
        oc3errorlocs = merged.loc[mask, "index3"]
        oc2errorlocs = merged.loc[mask, "index2"]
        return {"OC3": oc3errorlocs.tolist(), "OC2": oc2errorlocs.tolist()}


def test_validate():
    import pandas as pd

    fake_data_oc2 = pd.DataFrame(
        {
            "CHILD": ["A", "B", "C", "D", "E"],
            "IMMUNISATIONS": ["1", pd.NA, "1", pd.NA, "1"],
            "TEETH_CHECK": ["1", pd.NA, "1", "1", "1"],
            "HEALTH_ASSESSMENT": ["1", pd.NA, "1", pd.NA, "1"],
            "SUBSTANCE_MISUSE": [pd.NA, pd.NA, "1", "1", "1"],
            "CONVICTED": [pd.NA, pd.NA, "1", "1", pd.NA],
            "HEALTH_CHECK": [pd.NA, pd.NA, "1", "1", pd.NA],
            "INTERVENTION_RECEIVED": ["1", pd.NA, "1", "1", pd.NA],
            "INTERVENTION_OFFERED": [pd.NA, "1", "1", "1", pd.NA],
        }
    )
    fake_data_oc3 = pd.DataFrame(
        {
            "CHILD": ["A", "B", "C", "D", "E"],
            "IN_TOUCH": ["DIED", "Yes", "RHOM", pd.NA, pd.NA],
            "ACTIV": [pd.NA, pd.NA, "XXX", pd.NA, pd.NA],
            "ACCOM": [pd.NA, pd.NA, pd.NA, "XXX", pd.NA],
        }
    )
    fake_dfs = {"OC3": fake_data_oc3, "OC2": fake_data_oc2}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"OC3": [0, 1, 2, 3], "OC2": [0, 1, 2, 3]}
