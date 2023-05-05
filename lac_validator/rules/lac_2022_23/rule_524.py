from validator903.types import ErrorDefinition


@rule_definition(
    code="524",
    message="If reporting legal status of adopters is L12 then the genders of adopters should be coded as MM or FF. MM = the adopting couple are both males. FF = the adopting couple are both females",
    affected_fields=["LS_ADOPTR", "SEX_ADOPTR"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}

    else:
        AD1 = dfs["AD1"]

        errormask = AD1["LSADOPTR"].eq("L12") & ~AD1["SEXADOPTR"].isin(["MM", "FF"])

        errorlocations = AD1.index[errormask]

        return {"AD1": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS_ADOPTR": ["L12", "L12", pd.NA, "L12", "L12", "L4", "L12"],
            "SEX_ADOPTR": ["MM", "FF", "MM", "M1", "MF", "F1", "xxxxx"],
        }
    )

    fake_dfs = {"AD1": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"AD1": [3, 4, 6]}
