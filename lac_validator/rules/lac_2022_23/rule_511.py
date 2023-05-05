from validator903.types import ErrorDefinition


@rule_definition(
    code="511",
    message="If reporting that the number of person(s) adopting the looked after child is two adopters then the code should only be MM, FF or MF. MM = the adopting couple are both males; FF = the adopting couple are both females; MF = The adopting couple are male and female.",
    affected_fields=["NB_ADOPTR", "SEX_ADOPTR"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}

    else:
        AD1 = dfs["AD1"]

        mask = AD1["NBADOPTR"].astype(str).eq("2") & AD1["SEXADOPTR"].isin(["M1", "F1"])

        validationerrormask = mask
        validationerrorlocations = AD1.index[validationerrormask]

        return {"AD1": validationerrorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "NB_ADOPTR": ["2", "2", pd.NA, 2, "2", "1", 2, 1, 2],
            "SEX_ADOPTR": ["MM", "FF", "MM", "M1", "F1", "F1", "F1", "F1", pd.NA],
        }
    )

    fake_dfs = {"AD1": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"AD1": [3, 4, 6]}
