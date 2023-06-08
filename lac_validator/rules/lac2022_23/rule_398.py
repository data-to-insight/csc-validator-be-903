from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="398",
    message="Distance field completed but child looked after under legal status V3 or V4.",
    affected_fields=["LS", "HOME_POST", "PL_POST"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        mask = ((episodes["LS"] == "V3") | (episodes["LS"] == "V4")) & (
            episodes["HOME_POST"].notna() | episodes["PL_POST"].notna()
        )
        error_locations = episodes.index[mask]
        return {"Episodes": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "HOME_POST": [
                "AB1 0JD",
                "invalid",
                "AB1 0JD",
                "invalid",
                "AB10JD",
            ],
            "LS": ["V3", "U1", "V4", "T1", "U1"],
            "PL_POST": [
                "AB1 0JD",
                "AB1 0JD",
                pd.NA,
                "invalid",
                "AB1 0JD",
            ],
        }
    )
    fake_dfs = {"Episodes": fake_data}
    
    result = validate(fake_dfs)
    assert result == {"Episodes": [0, 2]}
