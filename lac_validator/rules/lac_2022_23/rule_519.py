from validator903.types import ErrorDefinition


@rule_definition(
    code="519",
    message="Data entered on the legal status of adopters shows civil partnership couple, but data entered on genders of adopters does not show it as a couple.",
    affected_fields=["LS_ADOPTR", "SEX_ADOPTR"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}
    else:
        ad1 = dfs["AD1"]
        mask = (ad1["LSADOPTR"] == "L2") & (
            (ad1["SEXADOPTR"] != "MM")
            & (ad1["SEXADOPTR"] != "FF")
            & (ad1["SEXADOPTR"] != "MF")
        )
        errorlocations = ad1.index[mask]
        return {"AD1": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS_ADOPTR": ["L2", "L4", pd.NA, "L2", "L2", "L2", "L4"],
            "SEX_ADOPTR": ["MM", "FF", "MM", "M1", "MF", pd.NA, "xxxxx"],
        }
    )

    fake_dfs = {"AD1": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"AD1": [3, 5]}
