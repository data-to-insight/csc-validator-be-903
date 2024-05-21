import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="159",
    message="If a child has been recorded as not receiving an intervention for their substance misuse problem, then the additional item on whether an intervention was offered should be completed as well.",
    affected_fields=[
        "SUBSTANCE_MISUSE",
        "INTERVENTION_RECEIVED",
        "INTERVENTION_OFFERED",
    ],
    tables=["OC2"],
)
def validate(dfs):
    if "OC2" not in dfs:
        return {}
    else:
        oc2 = dfs["OC2"]
        mask1 = oc2["SUBSTANCE_MISUSE"].astype(str) == "1"
        mask2 = oc2["INTERVENTION_RECEIVED"].astype(str) == "0"
        mask3 = oc2["INTERVENTION_OFFERED"].isna()

        validation_error = mask1 & mask2 & mask3
        validation_error_locations = oc2.index[validation_error]

        return {"OC2": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SUBSTANCE_MISUSE": ["1", "1", "1", "1", 1, "1", pd.NA, pd.NA, 1, 0],
            "INTERVENTION_RECEIVED": ["1", "0", "0", pd.NA, 0, "1", "1", pd.NA, 0, 1],
            "INTERVENTION_OFFERED": [
                pd.NA,
                "0",
                pd.NA,
                pd.NA,
                pd.NA,
                "1",
                pd.NA,
                pd.NA,
                0,
                1,
            ],
        }
    )

    fake_dfs = {"OC2": fake_data}

    result = validate(fake_dfs)

    assert result == {"OC2": [2, 4]}
