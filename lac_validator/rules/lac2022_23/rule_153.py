import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="153",
    message="All data items relating to a child's activity or accommodation after leaving care must be coded or left blank.",
    affected_fields=["IN_TOUCH", "ACTIV", "ACCOM"],
)
def validate(dfs):
    if "OC3" not in dfs:
        return {}

    oc3 = dfs["OC3"]

    oc3_not_na = oc3["IN_TOUCH"].notna() & oc3["ACTIV"].notna() & oc3["ACCOM"].notna()

    oc3_all_na = oc3["IN_TOUCH"].isna() & oc3["ACTIV"].isna() & oc3["ACCOM"].isna()

    validation_error = ~oc3_not_na & ~oc3_all_na

    validation_error_locations = oc3.index[validation_error]

    return {"OC3": validation_error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "IN_TOUCH": ["XXX", pd.NA, "XXX", pd.NA, pd.NA, "XXX"],
            "ACTIV": ["XXX", pd.NA, pd.NA, "XXX", pd.NA, "XXX"],
            "ACCOM": ["XXX", pd.NA, pd.NA, pd.NA, "XXX", pd.NA],
        }
    )

    fake_dfs = {"OC3": fake_data}

    result = validate(fake_dfs)

    assert result == {"OC3": [2, 3, 4, 5]}
