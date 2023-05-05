from validator903.types import ErrorDefinition


@rule_definition(
    code="158",
    message="If a child has been recorded as receiving an intervention for their substance misuse problem, then the additional item on whether an intervention was offered should be left blank.",
    affected_fields=["INTERVENTION_RECEIVED", "INTERVENTION_OFFERED"],
)
def validate(dfs):
    if "OC2" not in dfs:
        return {}

    else:
        oc2 = dfs["OC2"]

        errormask = (
            oc2["INTERVENTIONRECEIVED"].astype(str).eq("1")
            & oc2["INTERVENTIONOFFERED"].notna()
        )

        errorlocations = oc2.index[errormask]

        return {"OC2": errorlocations.tolist()}


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
