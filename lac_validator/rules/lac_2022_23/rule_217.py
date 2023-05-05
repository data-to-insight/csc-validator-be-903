import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="217",
    message="Children who are placed for adoption with current foster carers (placement types A3 or A5) must have a reason for new episode of S, T or U.",
    affected_fields=["PLACE", "DECOM", "RNE"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        episodes["DECOM"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        max_decom_allowed = pd.to_datetime(
            "01/04/2015", format="%d/%m/%Y", errors="coerce"
        )
        reason_new_ep = ["S", "T", "U"]
        place_codes = ["A3", "A5"]

        mask = (
            episodes["PLACE"].isin(place_codes)
            & (episodes["DECOM"] >= max_decom_allowed)
        ) & ~episodes["RNE"].isin(reason_new_ep)

        validation_error_mask = mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {"Episodes": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE": ["A3", "A5", "A3", pd.NA, "U1", "A3", "A5", "A5"],
            "DECOM": [
                "01/04/2015",
                "31/12/2015",
                "20/01/2016",
                pd.NA,
                "01/10/2017",
                "20/02/2016",
                "01/01/2017",
                "01/04/2013",
            ],
            "RNE": ["S", "T", "U", pd.NA, "X", "X", "X", "X"],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [5, 6]}
