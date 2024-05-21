import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="519",
    message="Data entered on the legal status of adopters shows civil partnership couple, but data entered on genders of adopters does not show it as a couple.",
    affected_fields=["LS_ADOPTR", "SEX_ADOPTR"],
    tables=["AD1"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}
    else:
        ad1 = dfs["AD1"]
        mask = (ad1["LS_ADOPTR"] == "L2") & (
            (ad1["SEX_ADOPTR"] != "MM")
            & (ad1["SEX_ADOPTR"] != "FF")
            & (ad1["SEX_ADOPTR"] != "MF")
        )
        error_locations = ad1.index[mask]
        return {"AD1": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS_ADOPTR": ["L2", "L4", pd.NA, "L2", "L2", "L2", "L4"],
            "SEX_ADOPTR": ["MM", "FF", "MM", "M1", "MF", pd.NA, "xxxxx"],
        }
    )

    fake_dfs = {"AD1": fake_data}

    result = validate(fake_dfs)

    assert result == {"AD1": [3, 5]}
