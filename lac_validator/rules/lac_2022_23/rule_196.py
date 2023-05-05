from validator903.types import ErrorDefinition


@rule_definition(
    code="196",
    message="Strengths and Difficulties (SDQ) reason is not a valid code.",
    affected_fields=["SDQ_REASON"],
)
def validate(dfs):
    if "OC2" not in dfs:
        return {}

    oc2 = dfs["OC2"]
    codelist = ["SDQ1", "SDQ2", "SDQ3", "SDQ4", "SDQ5"]

    mask = oc2["SDQREASON"].isin(codelist) | oc2["SDQREASON"].isna()

    validationerrormask = ~mask
    validationerrorlocations = oc2.index[validationerrormask]

    return {"OC2": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SDQ_REASON": ["SDQ2", "sdq2", "", pd.NA],
        }
    )

    fake_dfs = {"OC2": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"OC2": [1, 2]}
