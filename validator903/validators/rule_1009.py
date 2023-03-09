from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="1009",
        description="Reason for placement change is not a valid code.",
        affected_fields=["REASON_PLACE_CHANGE"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}

        episodes = dfs["Episodes"]
        code_list = [
            "CARPL",
            "CLOSE",
            "ALLEG",
            "STAND",
            "APPRR",
            "CREQB",
            "CREQO",
            "CHILD",
            "LAREQ",
            "PLACE",
            "CUSTOD",
            "OTHER",
        ]

        mask = (
            episodes["REASON_PLACE_CHANGE"].isin(code_list)
            | episodes["REASON_PLACE_CHANGE"].isna()
        )

        validation_error_mask = ~mask
        validation_error_locations = episodes.index[validation_error_mask]

        return {"Episodes": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "REASON_PLACE_CHANGE": ["CARPL", "OTHER", "other", "NA", "", pd.NA],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [2, 3, 4]}
