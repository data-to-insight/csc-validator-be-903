from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="144",
        description="The legal status code is not a valid code.",
        affected_fields=["LS"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}

        episodes = dfs["Episodes"]
        code_list = [
            "C1",
            "C2",
            "D1",
            "E1",
            "V2",
            "V3",
            "V4",
            "J1",
            "J2",
            "J3",
            "L1",
            "L2",
            "L3",
        ]

        mask = episodes["LS"].isin(code_list) | episodes["LS"].isna()

        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {"Episodes": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "LS": ["C1", "c1", "section 20", "", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1, 2, 3]}
