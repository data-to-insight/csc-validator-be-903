import pandas as pd

from lac_validator.rule_engine import rule_definition


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
        mask = (ad1["LS_ADOPTR"] == "L11") & (ad1["SEX_ADOPTR"] != "MF")
        error_locations = ad1.index[mask]
        return {"AD1": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_ad1 = pd.DataFrame(
        {
            "LS_ADOPTR": ["L11", "L11", pd.NA, "L4", "L11", "L1", "L4"],
            "SEX_ADOPTR": ["MM", "FF", "MM", "M1", "MF", "F1", "xxxxx"],
        }
    )
    fake_dfs = {"AD1": fake_ad1}

    result = validate(fake_dfs)
    assert result == {"AD1": [0, 1]}
