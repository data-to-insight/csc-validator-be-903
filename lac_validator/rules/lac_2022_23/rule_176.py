from validator903.types import ErrorDefinition


@rule_definition(
    code="176",
    message="The gender of adopter(s) at the date of adoption code is not a valid code.",
    affected_fields=["SEX_ADOPTR"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}

    adoptions = dfs["AD1"]
    codelist = ["M1", "F1", "MM", "FF", "MF"]

    mask = adoptions["SEXADOPTR"].isin(codelist) | adoptions["SEXADOPTR"].isna()

    validationerrormask = ~mask
    validationerrorlocations = adoptions.index[validationerrormask]

    return {"AD1": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SEX_ADOPTR": ["m1", "F1", "MM", "1", "", pd.NA],
        }
    )

    fake_dfs = {"AD1": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"AD1": [0, 3, 4]}
