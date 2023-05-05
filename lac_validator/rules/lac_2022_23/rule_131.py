from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="131",
    message="Data entry for being in touch after leaving care is invalid.",
    affected_fields=["IN_TOUCH"],
)
def validate(dfs):
    if "OC3" not in dfs:
        return {}

    care_leavers = dfs["OC3"]
    code_list = ["YES", "NO", "DIED", "REFU", "NREQ", "RHOM"]
    mask = care_leavers["IN_TOUCH"].isin(code_list)

    validation_error_mask = ~mask
    validation_error_locations = care_leavers.index[validation_error_mask]

    return {"OC3": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "IN_TOUCH": ["yes", "YES", 1, "REFUSE", "REFU", "", pd.NA],
        }
    )

    fake_dfs = {"OC3": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC3": [0, 2, 3, 5, 6]}
