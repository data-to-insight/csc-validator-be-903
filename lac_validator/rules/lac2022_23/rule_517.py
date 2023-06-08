from lac_validator.rule_engine import rule_definition


import pandas as pd


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

        error_mask = AD1["LS_ADOPTR"].eq("L3") & ~AD1["SEX_ADOPTR"].isin(["MF"])

        error_locations = AD1.index[error_mask]

        return {"AD1": error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS_ADOPTR": ["L3", "L1", pd.NA, "L3", "L3", "L4", "L3"],
            "SEX_ADOPTR": ["MF", "MF", "MM", "M1", "FF", "F1", "xxxxx"],
        }
    )

    fake_dfs = {"AD1": fake_data}

    

    result = validate(fake_dfs)

    assert result == {"AD1": [3, 4, 6]}
