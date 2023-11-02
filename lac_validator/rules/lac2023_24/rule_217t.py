import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="217",
    message="Placement type 'P2' is not a valid placement type from 28 October 2023.",
    affected_fields=["PLACE", "DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        episodes["DEC"] = pd.to_datetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )
        max_dec_allowed = pd.to_datetime(
            "28/10/2023", format="%d/%m/%Y", errors="coerce"
        )

        mask = (
            episodes["PLACE"].isin(["P2"])
            & (
                (episodes["DEC"] > max_dec_allowed) | episodes["DEC"].isna()
            )
        )

        validation_error_mask = mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {"Episodes": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE": ["P2", "P2", "P2", "P1"],
            "DEC": [
                "01/11/2023", # Fail (After code end date)
                "28/10/2023", # Pass (On code end date)
                pd.NA, # Fail (Nil end after code end date)
                "01/11/2023", # Ignore (Not P2)
            ],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [0, 2]}
