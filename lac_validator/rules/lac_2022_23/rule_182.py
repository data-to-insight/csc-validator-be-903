from lac_validator.rule_engine import rule_definition


import pandas as pd


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
            | oc2["TEETH_CHECK"].isna()
            | oc2["HEALTH_ASSESSMENT"].isna()
            | oc2["SUBSTANCE_MISUSE"].isna()
        )
        mask2 = (
            oc2["CONVICTED"].isna()
            & oc2["HEALTH_CHECK"].isna()
            & oc2["INTERVENTION_RECEIVED"].isna()
            & oc2["INTERVENTION_OFFERED"].isna()
        )

        validation_error = mask1 & ~mask2
        validation_error_locations = oc2.index[validation_error]

        return {"OC2": validation_error_locations.tolist()}


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
