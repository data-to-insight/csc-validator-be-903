import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="113",
        description="Date matching child and adopter(s) is not a valid date.",
        affected_fields=["DATE_MATCH"],
    )

    def _validate(dfs):
        if "AD1" not in dfs:
            return {}
        else:
            ad1 = dfs["AD1"]
            mask = pd.to_datetime(
                ad1["DATE_MATCH"], format="%d/%m/%Y", errors="coerce"
            ).notna()

            na_location = ad1["DATE_MATCH"].isna()

            validation_error_mask = ~mask & ~na_location
            validation_error_locations = ad1.index[validation_error_mask]

            return {"AD1": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "DATE_MATCH": ["22/11/2015", "08/05/2010", "38/04/2019", "01/01/19", pd.NA],
        }
    )

    fake_dfs = {"AD1": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"AD1": [2, 3]}
