from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="530",
        description="A placement provider code of PR4 cannot be associated with placement P1.",
        affected_fields=["PLACE", "PLACE_PROVIDER"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}
        else:
            episodes = dfs["Episodes"]
            mask = episodes["PLACE"].eq("P1") & episodes["PLACE_PROVIDER"].eq("PR4")

            validation_error_mask = mask
            validation_error_locations = episodes.index[validation_error_mask]

            return {"Episodes": validation_error_locations.tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "PLACE": ["P1", "A3", "K1", "P1", "P1", "P1"],
            "PLACE_PROVIDER": ["PR4", "PR3", "PR4", "PR4", "PR5", "PRO"],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 3]}
