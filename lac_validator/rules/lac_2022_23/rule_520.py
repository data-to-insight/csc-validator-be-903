from validator903.types import ErrorDefinition


@rule_definition(
    code="520",
    message="Data entry on the legal status of adopters shows different gender married couple but data entry on genders of adopters shows it as a same gender couple.",
    affected_fields=["LS_ADOPTR", "SEX_ADOPTR"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}
    else:
        ad1 = dfs["AD1"]
        # check condition
        mask = (ad1["LSADOPTR"] == "L11") & (ad1["SEXADOPTR"] != "MF")
        errorlocations = ad1.index[mask]
        return {"AD1": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_ad1 = pd.DataFrame(
        {
            "LS_ADOPTR": ["L11", "L11", pd.NA, "L4", "L11", "L1", "L4"],
            "SEX_ADOPTR": ["MM", "FF", "MM", "M1", "MF", "F1", "xxxxx"],
        }
    )
    fake_dfs = {"AD1": fake_ad1}
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"AD1": [0, 1]}
