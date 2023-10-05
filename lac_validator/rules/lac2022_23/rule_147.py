import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="147",
    message="Date episode ceased is not a valid date.",
    affected_fields=["DEC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        mask = pd.to_datetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        ).notna()

        na_location = episodes["DEC"].isna()

        validation_error_mask = ~mask & ~na_location
        validation_error_locations = episodes.index[validation_error_mask]

        return {"Episodes": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DEC": ["01/01/2021", "19/02/2010", "38/04/2019", "01/01/19", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    result = validate(fake_dfs)

    assert result == {"Episodes": [2, 3]}
