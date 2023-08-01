from lac_validator.rule_engine import rule_definition


import pandas as pd


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
        code_list = ["0", "1"]

        fields_of_interest = [
            "CONVICTED",
            "HEALTH_CHECK",
            "IMMUNISATIONS",
            "TEETH_CHECK",
            "HEALTH_ASSESSMENT",
            "SUBSTANCE_MISUSE",
            "INTERVENTION_RECEIVED",
            "INTERVENTION_OFFERED",
        ]

        error_mask = (
            oc2[fields_of_interest].notna()
            & ~oc2[fields_of_interest].astype(str).isin(["0", "1"])
        ).any(axis=1)

        validation_error_locations = oc2.index[error_mask]

        return {"OC2": validation_error_locations.tolist()}


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

    

    result = validate(fake_dfs)

    assert result == {"OC2": [3, 4]}
