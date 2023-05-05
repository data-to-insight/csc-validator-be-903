from validator903.types import ErrorDefinition


@rule_definition(
    code="517",
    message="If reporting legal status of adopters is L3 then the genders of adopters should be coded as MF. MF = the adopting couple are male and female.",
    affected_fields=["LS_ADOPTR", "SEX_ADOPTR"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}

    else:
        AD1 = dfs["AD1"]

        errormask = AD1["LSADOPTR"].eq("L3") & ~AD1["SEXADOPTR"].isin(["MF"])

        errorlocations = AD1.index[errormask]

        return {"AD1": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS_ADOPTR": ["L3", "L1", pd.NA, "L3", "L3", "L4", "L3"],
            "SEX_ADOPTR": ["MF", "MF", "MM", "M1", "FF", "F1", "xxxxx"],
        }
    )

    fake_dfs = {"AD1": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"AD1": [3, 4, 6]}
