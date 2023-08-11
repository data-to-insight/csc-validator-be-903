import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="116",
    message="Date of Local Authority's (LA) decision that a child should no longer be placed for adoption is not a valid date.",
    affected_fields=["DATE_PLACED_CEASED"],
)
def validate(dfs):
    if "PlacedAdoption" not in dfs:
        return {}
    else:
        adopt = dfs["PlacedAdoption"]
        mask = pd.to_datetime(
            adopt["DATE_PLACED_CEASED"], format="%d/%m/%Y", errors="coerce"
        ).notna()

        na_location = adopt["DATE_PLACED_CEASED"].isna()

        validation_error_mask = ~mask & ~na_location
        validation_error_locations = adopt.index[validation_error_mask]

        return {"PlacedAdoption": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DATE_PLACED_CEASED": [
                "01/01/2021",
                "19/02/2010",
                "38/04/2019",
                "01/01/19",
                pd.NA,
            ],
        }
    )

    fake_dfs = {"PlacedAdoption": fake_data}

    result = validate(fake_dfs)

    assert result == {"PlacedAdoption": [2, 3]}
