from validator903.types import ErrorDefinition


@rule_definition(
    code="193",
    message="Child not identified as having a substance misuse problem but at least one of the two additional items on whether an intervention were offered and received have been completed.",
    affected_fields=[
        "SUBSTANCE_MISUSE",
        "INTERVENTION_RECEIVED",
        "INTERVENTION_OFFERED",
    ],
)
def validate(dfs):
    if "OC2" not in dfs:
        return {}
    else:
        oc2 = dfs["OC2"]

        nosubstancemisuse = oc2["SUBSTANCEMISUSE"].isna() | (
            oc2["SUBSTANCEMISUSE"].astype(str) == "0"
        )
        interventionnotblank = (
            oc2["INTERVENTIONRECEIVED"].notna() | oc2["INTERVENTIONOFFERED"].notna()
        )

        errormask = nosubstancemisuse & interventionnotblank
        validationerrorlocations = oc2.index[errormask]

        return {"OC2": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SUBSTANCE_MISUSE": [0, pd.NA, 0, "1", pd.NA, pd.NA, 0],
            "INTERVENTION_RECEIVED": [0, pd.NA, "1", 1, "1", pd.NA, pd.NA],
            "INTERVENTION_OFFERED": [0, pd.NA, "1", 1, pd.NA, 0, pd.NA],
        }
    )

    fake_dfs = {"OC2": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC2": [0, 2, 4, 5]}
