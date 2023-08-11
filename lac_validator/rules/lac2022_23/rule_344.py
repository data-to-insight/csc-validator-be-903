import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="344",
    message="The record shows the young person has died or returned home to live with parent(s) or someone with parental responsibility for a continuous period of 6 months or more, but activity and/or accommodation on leaving care have been completed.",
    affected_fields=["IN_TOUCH", "ACTIV", "ACCOM"],
)
def validate(dfs):
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

    result = validate(fake_dfs)
    assert result == {"OC3": [2, 4, 5]}
