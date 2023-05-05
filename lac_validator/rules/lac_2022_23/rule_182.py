from validator903.types import ErrorDefinition


@rule_definition(
    code="182",
    message="Data entries on immunisations, teeth checks, health assessments and substance misuse problem identified should be completed or all OC2 fields should be left blank.",
    affected_fields=[
        "IMMUNISATIONS",
        "TEETH_CHECK",
        "HEALTH_ASSESSMENT",
        "SUBSTANCE_MISUSE",
        "CONVICTED",
        "HEALTH_CHECK",
        "INTERVENTION_RECEIVED",
        "INTERVENTION_OFFERED",
    ],
)
def validate(dfs):
    if "OC2" not in dfs:
        return {}
    else:
        oc2 = dfs["OC2"]

        mask1 = (
            oc2["IMMUNISATIONS"].isna()
            | oc2["TEETHCHECK"].isna()
            | oc2["HEALTHASSESSMENT"].isna()
            | oc2["SUBSTANCEMISUSE"].isna()
        )
        mask2 = (
            oc2["CONVICTED"].isna()
            & oc2["HEALTHCHECK"].isna()
            & oc2["INTERVENTIONRECEIVED"].isna()
            & oc2["INTERVENTIONOFFERED"].isna()
        )

        validationerror = mask1 & ~mask2
        validationerrorlocations = oc2.index[validationerror]

        return {"OC2": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "IMMUNISATIONS": [pd.NA, pd.NA, pd.NA, "1", pd.NA, "1", pd.NA, "1"],
            "TEETH_CHECK": [pd.NA, pd.NA, pd.NA, "1", pd.NA, "1", "1", "1"],
            "HEALTH_ASSESSMENT": [pd.NA, pd.NA, pd.NA, "1", pd.NA, "1", pd.NA, "1"],
            "SUBSTANCE_MISUSE": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "1", "1", "1"],
            "CONVICTED": [pd.NA, "1", pd.NA, pd.NA, pd.NA, "1", "1", pd.NA],
            "HEALTH_CHECK": [pd.NA, pd.NA, "1", pd.NA, pd.NA, "1", "1", pd.NA],
            "INTERVENTION_RECEIVED": [pd.NA, pd.NA, pd.NA, "1", pd.NA, "1", "1", pd.NA],
            "INTERVENTION_OFFERED": [pd.NA, pd.NA, pd.NA, pd.NA, "1", "1", "1", pd.NA],
        }
    )

    fake_dfs = {"OC2": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)
    assert result == {"OC2": [1, 2, 3, 4, 6]}
