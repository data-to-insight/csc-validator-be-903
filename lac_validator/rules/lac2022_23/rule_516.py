import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="516",
    message="The episode data submitted for this child does not show that he/she was with their former foster carer(s) during the year.If the code in the reason episode ceased is E45 or E46 the child must have a placement code of U1 to U6.",
    affected_fields=["REC", "PLACE"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}

    else:
        episodes = dfs["Episodes"]
        place_codes = ["U1", "U2", "U3", "U4", "U5", "U6"]
        rec_codes = ["E45", "E46"]

        error_mask = episodes["REC"].isin(rec_codes) & ~episodes["PLACE"].isin(
            place_codes
        )

        validation_error_locations = episodes.index[error_mask]

        return {"Episodes": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "REC": [
                "E45",
                "E46",
                pd.NA,
                "E45",
                "E46",
                "E45",
                "E45",
                "E2",
                "E2",
                "E46",
                "E46",
                "E46",
            ],
            "PLACE": [
                "U1",
                "U2",
                "U3",
                "Z1",
                "S1",
                "R1",
                "U4",
                "K2",
                "K2",
                "T1",
                "U6",
                "xx",
            ],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [3, 4, 5, 9, 11]}
