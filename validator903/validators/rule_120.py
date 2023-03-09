from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="120",
        description="The reason for the reversal of the decision that the child should be placed for adoption code is not valid.",
        affected_fields=["REASON_PLACED_CEASED"],
    )

    def _validate(dfs):
        if "PlacedAdoption" not in dfs:
            return {}

        placed_adoptions = dfs["PlacedAdoption"]
        code_list = ["RD1", "RD2", "RD3", "RD4"]

        mask = (
            placed_adoptions["REASON_PLACED_CEASED"].isin(code_list)
            | placed_adoptions["REASON_PLACED_CEASED"].isna()
        )

        validation_error_mask = ~mask
        validation_error_locations = placed_adoptions.index[validation_error_mask]

        return {"PlacedAdoption": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "REASON_PLACED_CEASED": ["rd1", "RD0", 1, "RD1", "", pd.NA],
        }
    )

    fake_dfs = {"PlacedAdoption": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"PlacedAdoption": [0, 1, 2, 4]}
