from validator903.types import ErrorDefinition


@rule_definition(
    code="153",
    message="All data items relating to a child's activity or accommodation after leaving care must be coded or left blank.",
    affected_fields=["IN_TOUCH", "ACTIV", "ACCOM"],
)
def validate(dfs):
    if "OC3" not in dfs:
        return {}

    oc3 = dfs["OC3"]

    oc3notna = oc3["INTOUCH"].notna() & oc3["ACTIV"].notna() & oc3["ACCOM"].notna()

    oc3allna = oc3["INTOUCH"].isna() & oc3["ACTIV"].isna() & oc3["ACCOM"].isna()

    validationerror = ~oc3notna & ~oc3allna

    validationerrorlocations = oc3.index[validationerror]

    return {"OC3": validationerrorlocations.tolist()}


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

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC3": [2, 3, 4, 5]}
