from validator903.types import ErrorDefinition


@rule_definition(
    code="345",
    message="The data collection record shows the local authority is in touch with this young person, but activity and/or accommodation data items are zero.",
    affected_fields=["IN_TOUCH", "ACTIV", "ACCOM"],
)
def validate(dfs):
    if "OC3" not in dfs:
        return {}
    else:
        oc3 = dfs["OC3"]
        # If <INTOUCH> = 'Yes' then <ACTIV> and <ACCOM> must not be 0
        mask = (oc3["INTOUCH"] == "YES") & (
            (oc3["ACTIV"].astype(str) == "0") | (oc3["ACCOM"].astype(str) == "0")
        )
        errorlocations = oc3.index[mask]
        return {"OC3": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data_oc3 = pd.DataFrame(
        {
            "CHILD": ["A", "B", "C", "D", "E"],
            "IN_TOUCH": ["No", "YES", "YES", pd.NA, "Yes"],
            "ACTIV": [pd.NA, 0, "XXX", pd.NA, "XXX"],
            "ACCOM": [0, pd.NA, "0", "XXX", "XXX"],
        }
    )
    fake_dfs = {"OC3": fake_data_oc3}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"OC3": [1, 2]}
