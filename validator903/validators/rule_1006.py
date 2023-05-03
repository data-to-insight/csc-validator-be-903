from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="1006",
        description="Missing type invalid.",
        affected_fields=["MISSING"],
    )

    def _validate(dfs):
        if "Missing" not in dfs:
            return {}

        missing_from_care = dfs["Missing"]
        code_list = ["M", "A"]

        mask = (
            missing_from_care["MISSING"].isin(code_list)
            | missing_from_care["MISSING"].isna()
        )

        validation_error_mask = ~mask
        validation_error_locations = missing_from_care.index[validation_error_mask]

        return {"Missing": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "MISSING": ["M", "A", "AWAY", "NA", "", pd.NA],
        }
    )

    fake_dfs = {"Missing": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Missing": [2, 3, 4]}
