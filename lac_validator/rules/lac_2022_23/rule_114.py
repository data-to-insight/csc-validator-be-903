from validator903.types import ErrorDefinition


@rule_definition(
    code="114",
    message="Data entry to record the status of former carer(s) of an adopted child is invalid.",
    affected_fields=["FOSTER_CARE"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}

    adoptions = dfs["AD1"]
    codelist = ["0", "1"]

    mask = (
        adoptions["FOSTERCARE"].astype(str).isin(codelist)
        | adoptions["FOSTERCARE"].isna()
    )

    validationerrormask = ~mask
    validationerrorlocations = adoptions.index[validationerrormask]

    return {"AD1": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "FOSTER_CARE": [0, 1, "0", "1", 2, "former foster carer", "", pd.NA],
        }
    )

    fake_dfs = {"AD1": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"AD1": [4, 5, 6]}
