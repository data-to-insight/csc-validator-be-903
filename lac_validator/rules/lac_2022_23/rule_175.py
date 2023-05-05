from validator903.types import ErrorDefinition


@rule_definition(
    code="175",
    message="The number of adopter(s) code is not a valid code.",
    affected_fields=["NB_ADOPTR"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}

    adoptions = dfs["AD1"]
    codelist = ["1", "2"]

    mask = (
        adoptions["NBADOPTR"].astype(str).isin(codelist) | adoptions["NBADOPTR"].isna()
    )

    validationerrormask = ~mask
    validationerrorlocations = adoptions.index[validationerrormask]

    return {"AD1": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "NB_ADOPTR": [0, 1, 2, "1", "2", "0", "", pd.NA],
        }
    )

    fake_dfs = {"AD1": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"AD1": [0, 5, 6]}
