import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="184",
    message="Date of decision that a child should be placed for adoption is before the child was born.",
    affected_fields=["DATE_PLACED", "DOB"],  # PlacedAdoptino  # Header
    tables=["Header", "PlacedAdoption"],
)
def validate(dfs):
    if "Header" not in dfs or "PlacedAdoption" not in dfs:
        return {}
    else:
        child_record = dfs["Header"]
        placed_for_adoption = dfs["PlacedAdoption"]

        all_data = placed_for_adoption.reset_index().merge(
            child_record, how="left", on="CHILD", suffixes=[None, "_P4A"]
        )

        all_data["DATE_PLACED"] = pd.to_datetime(
            all_data["DATE_PLACED"], format="%d/%m/%Y", errors="coerce"
        )
        all_data["DOB"] = pd.to_datetime(
            all_data["DOB"], format="%d/%m/%Y", errors="coerce"
        )

        mask = (all_data["DATE_PLACED"] >= all_data["DOB"]) | all_data[
            "DATE_PLACED"
        ].isna()

        validation_error = ~mask

        validation_error_locations = all_data[validation_error]["index"].unique()

        return {"PlacedAdoption": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data_header = pd.DataFrame(
        {
            "CHILD": ["111", "112", "113", "114"],
            "DOB": ["01/10/2017", "31/05/2018", "10/03/2019", "19/08/2020"],
        }
    )
    fake_data_placed = pd.DataFrame(
        {
            "CHILD": ["111", "112", "113", "114"],
            "DATE_PLACED": ["01/10/2017", "10/02/2019", "10/02/2019", pd.NA],
        }
    )

    fake_dfs = {"Header": fake_data_header, "PlacedAdoption": fake_data_placed}

    result = validate(fake_dfs)

    assert result == {"PlacedAdoption": [2]}
