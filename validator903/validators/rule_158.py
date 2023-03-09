from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="158",
        description="If a child has been recorded as receiving an intervention for their substance misuse problem, then the additional item on whether an intervention was offered should be left blank.",
        affected_fields=["INTERVENTION_RECEIVED", "INTERVENTION_OFFERED"],
    )

    def _validate(dfs):
        if "OC2" not in dfs:
            return {}

        else:
            oc2 = dfs["OC2"]

            error_mask = (
                oc2["INTERVENTION_RECEIVED"].astype(str).eq("1")
                & oc2["INTERVENTION_OFFERED"].notna()
            )

            error_locations = oc2.index[error_mask]

            return {"OC2": error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "INTERVENTION_RECEIVED": ["1", pd.NA, "0", "1", "1", "0"],
            "INTERVENTION_OFFERED": [pd.NA, "1", "0", "1", "0", "1"],
        }
    )

    fake_dfs = {"OC2": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC2": [3, 4]}
