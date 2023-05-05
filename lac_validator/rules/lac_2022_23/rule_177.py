from validator903.types import ErrorDefinition


@rule_definition(
    code="177",
    message="The legal status of adopter(s) code is not a valid code.",
    affected_fields=["LS_ADOPTR"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}

    adoptions = dfs["AD1"]
    codelist = ["L0", "L11", "L12", "L2", "L3", "L4"]

    mask = adoptions["LSADOPTR"].isin(codelist) | adoptions["LSADOPTR"].isna()

    validationerrormask = ~mask
    validationerrorlocations = adoptions.index[validationerrormask]

    return {"AD1": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS_ADOPTR": ["L0", "L11", "L1", "l2", "", pd.NA],
        }
    )

    fake_dfs = {"AD1": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"AD1": [2, 3, 4]}
