import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="112",
    message="Date should be placed for adoption is not a valid date.",
    affected_fields=["DATE_INT"],
)
def validate(dfs):
    if "AD1" not in dfs:
        return {}
    else:
        ad1 = dfs["AD1"]
        mask = pd.to_datetime(
            ad1["DATE_INT"], format="%d/%m/%Y", errors="coerce"
        ).notna()

        na_location = ad1["DATE_INT"].isna()

        validation_error_mask = ~mask & ~na_location
        validation_error_locations = ad1.index[validation_error_mask]

        return {"AD1": validation_error_locations.tolist()}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DATE_INT": ["01/01/2021", "19/02/2010", "38/04/2019", "01/01/19", pd.NA],
        }
    )

    fake_dfs = {"AD1": fake_data}

    result = validate(fake_dfs)

    assert result == {"AD1": [2, 3]}
