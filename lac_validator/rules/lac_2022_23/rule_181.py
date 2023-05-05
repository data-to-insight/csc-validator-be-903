from validator903.types import ErrorDefinition


@rule_definition(
    code="181",
    message="Data items relating to children looked after continuously for 12 months should be completed with a 0 or 1.",
    affected_fields=[
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
    if "OC2" not in dfs:
        return {}
    else:
        oc2 = dfs["OC2"]
        codelist = ["0", "1"]

        fieldsofinterest = [
            "CONVICTED",
            "HEALTHCHECK",
            "IMMUNISATIONS",
            "TEETHCHECK",
            "HEALTHASSESSMENT",
            "SUBSTANCEMISUSE",
            "INTERVENTIONRECEIVED",
            "INTERVENTIONOFFERED",
        ]

        errormask = (
            oc2[fieldsofinterest].notna()
            & ~oc2[fieldsofinterest].astype(str).isin(["0", "1"])
        ).any(axis=1)

        validationerrorlocations = oc2.index[errormask]

        return {"OC2": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CONVICTED": [1, pd.NA, pd.NA, "2", "2"],
            "HEALTH_CHECK": [1, pd.NA, pd.NA, 2, "2"],
            "IMMUNISATIONS": [1, pd.NA, pd.NA, pd.NA, "2"],
            "TEETH_CHECK": ["1", pd.NA, "0", pd.NA, "2"],
            "HEALTH_ASSESSMENT": ["1", pd.NA, 1, pd.NA, "2"],
            "SUBSTANCE_MISUSE": [0, pd.NA, 0, "1", "2"],
            "INTERVENTION_RECEIVED": [0, pd.NA, "1", 1, "2"],
            "INTERVENTION_OFFERED": ["1", pd.NA, pd.NA, 0, "2"],
        }
    )

    fake_dfs = {"OC2": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC2": [3, 4]}
