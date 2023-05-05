from validator903.types import ErrorDefinition


@rule_definition(
    code="514",
    message="Data entry on the legal status of adopters shows a single adopter but data entry for the numbers of adopters shows it as a couple.",
    affected_fields=["LS_ADOPTR", "SEX_ADOPTR"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}
    else:
        AD1 = dfs["AD1"]
        codelist = ["M1", "F1"]
        # Check if LS Adopter is L0 and Sex Adopter is not M1 or F1.
        errormask = (AD1["LSADOPTR"] == "L0") & (~AD1["SEXADOPTR"].isin(codelist))

        errorlocations = AD1.index[errormask]

        return {"AD1": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS_ADOPTR": ["L0", "xx", "L0", pd.NA, "L0"],
            "SEX_ADOPTR": ["M1", "F1", "xx", pd.NA, "xxx"],
        }
    )

    fake_dfs = {"AD1": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {
        "AD1": [
            2,
            4,
        ]
    }
