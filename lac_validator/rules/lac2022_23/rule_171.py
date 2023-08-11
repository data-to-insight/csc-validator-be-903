import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="171",
    message="Date of birth of mother's child is not a valid date.",
    affected_fields=["MC_DOB"],
)
def validate(dfs):
    if "Header" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        mask = pd.to_datetime(
            header["MC_DOB"], format="%d/%m/%Y", errors="coerce"
        ).notna()

        na_location = header["MC_DOB"].isna()

        validation_error_mask = ~mask & ~na_location
        validation_error_locations = header.index[validation_error_mask]

        return {"Header": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "MC_DOB": ["01/01/2021", "19/02/2010", "38/04/2019", "01/01/19", pd.NA],
        }
    )

    fake_dfs = {"Header": fake_data}

    result = validate(fake_dfs)

    assert result == {"Header": [2, 3]}
