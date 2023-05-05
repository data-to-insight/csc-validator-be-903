from validator903.types import ErrorDefinition


@rule_definition(
    code="192",
    message="Child has been identified as having a substance misuse problem but the additional item on whether an intervention was received has been left blank.",
    affected_fields=["SUBSTANCE_MISUSE", "INTERVENTION_RECEIVED"],
)
def validate(dfs):
    if "OC2" not in dfs:
        return {}
    else:
        oc2 = dfs["OC2"]

        misuse = oc2["SUBSTANCEMISUSE"].astype(str) == "1"
        interventionblank = oc2["INTERVENTIONRECEIVED"].isna()

        errormask = misuse & interventionblank
        validationerrorlocations = oc2.index[errormask]

        return {"OC2": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SUBSTANCE_MISUSE": [0, pd.NA, 0, "1", 1, "1"],
            "INTERVENTION_RECEIVED": [0, pd.NA, "1", 1, pd.NA, pd.NA],
        }
    )

    fake_dfs = {"OC2": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC2": [4, 5]}
