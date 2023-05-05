from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="518",
    message="If reporting legal status of adopters is L4 then the genders of adopters should be coded as MM or FF. MM = the adopting couple are both males. FF = the adopting couple are both females.",
    affected_fields=["LS_ADOPTR", "SEX_ADOPTR"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}

    else:
        AD1 = dfs["AD1"]

        error_mask = AD1["LS_ADOPTR"].eq("L4") & ~AD1["SEX_ADOPTR"].isin(["MM", "FF"])

        error_locations = AD1.index[error_mask]

        return {"AD1": error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS_ADOPTR": ["L4", "L4", pd.NA, "L4", "L4", "L1", "L4"],
            "SEX_ADOPTR": ["MM", "FF", "MM", "M1", "MF", "F1", "xxxxx"],
        }
    )

    fake_dfs = {"AD1": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"AD1": [3, 4, 6]}
