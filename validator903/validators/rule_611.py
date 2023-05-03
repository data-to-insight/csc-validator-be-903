from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="611",
        description="Date of birth field is blank, but child is a mother.",
        affected_fields=["MOTHER", "MC_DOB"],
    )

    def _validate(dfs):
        if "Header" not in dfs:
            return {}
        else:
            header = dfs["Header"]
            validation_error_mask = (
                header["MOTHER"].astype(str).isin(["1"]) & header["MC_DOB"].isna()
            )
            validation_error_locations = header.index[validation_error_mask]

            return {"Header": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "MOTHER": [1, "1", pd.NA, pd.NA, 1],
            "MC_DOB": ["01/01/2021", "19/02/2016", "dd/mm/yyyy", "31/31/19", pd.NA],
        }
    )

    fake_dfs = {"Header": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [4]}
