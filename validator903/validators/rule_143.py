from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="143",
        description="The reason for new episode code is not a valid code.",
        affected_fields=["RNE"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}

        episodes = dfs["Episodes"]
        code_list = ["S", "P", "L", "T", "U", "B"]

        mask = episodes["RNE"].isin(code_list) | episodes["RNE"].isna()

        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {"Episodes": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "RNE": ["S", "p", "SP", "a", "", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1, 2, 3, 4]}
