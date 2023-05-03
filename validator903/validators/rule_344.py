from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="344",
        description="The record shows the young person has died or returned home to live with parent(s) or someone with parental responsibility for a continuous period of 6 months or more, but activity and/or accommodation on leaving care have been completed.",
        affected_fields=["IN_TOUCH", "ACTIV", "ACCOM"],
    )

    def _validate(dfs):
        if "OC3" not in dfs:
            return {}
        else:
            oc3 = dfs["OC3"]
            # If <IN_TOUCH> = 'DIED' or 'RHOM' then <ACTIV> and <ACCOM> should not be provided (0 for this)
            mask = ((oc3["IN_TOUCH"] == "DIED") | (oc3["IN_TOUCH"] == "RHOM")) & (
                (oc3["ACTIV"].astype(str) != "0") | (oc3["ACCOM"].astype(str) != "0")
            )
            error_locations = oc3.index[mask]
            return {"OC3": error_locations.to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data_oc3 = pd.DataFrame(
        {
            "CHILD": ["A", "B", "C", "D", "E", "F"],
            "IN_TOUCH": ["DIED", "Yes", "RHOM", pd.NA, "DIED", "RHOM"],
            "ACTIV": ["0", pd.NA, "XXX", pd.NA, "XXX", pd.NA],
            "ACCOM": [0, pd.NA, 0, "XXX", "XXX", 0],
        }
    )
    fake_dfs = {"OC3": fake_data_oc3}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"OC3": [2, 4, 5]}
