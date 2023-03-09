from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="145",
        description="Category of need code is not a valid code.",
        affected_fields=["CIN"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}

        episodes = dfs["Episodes"]
        code_list = [
            "N1",
            "N2",
            "N3",
            "N4",
            "N5",
            "N6",
            "N7",
            "N8",
        ]

        mask = episodes["CIN"].isin(code_list) | episodes["CIN"].isna()
        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {"Episodes": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "CIN": ["N0", "N1", "N9", "n8", "", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 2, 3, 4]}
