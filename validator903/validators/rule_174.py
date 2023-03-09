from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="174",
        description="Mother's child date of birth is recorded but gender shows that the child is a male.",
        affected_fields=["SEX", "MC_DOB"],
    )

    def _validate(dfs):
        if "Header" not in dfs:
            return {}
        else:
            header = dfs["Header"]

            child_is_male = header["SEX"].astype(str) == "1"
            mc_dob_recorded = header["MC_DOB"].notna()

            error_mask = child_is_male & mc_dob_recorded

            validation_error_locations = header.index[error_mask]

            return {"Header": validation_error_locations.to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "SEX": ["1", "1", "2", "2", 1, 1],
            "MC_DOB": [pd.NA, "19/02/2010", pd.NA, "19/02/2010", pd.NA, "19/02/2010"],
        }
    )

    fake_dfs = {"Header": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Header": [1, 5]}
