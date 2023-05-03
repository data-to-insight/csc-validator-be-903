from validator903.types import ErrorDefinition
from validator903.datastore import merge_postcodes


def validate():
    error = ErrorDefinition(
        code="392c",
        description="Postcode(s) provided are invalid.",
        affected_fields=["HOME_POST", "PL_POST"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs:
            return {}
        else:
            episodes = dfs["Episodes"]

            home_provided = episodes["HOME_POST"].notna()
            home_details = merge_postcodes(episodes, "HOME_POST")
            home_valid = home_details["pcd"].notna()

            pl_provided = episodes["PL_POST"].notna()
            pl_details = merge_postcodes(episodes, "PL_POST")
            pl_valid = pl_details["pcd"].notna()

            error_mask = (home_provided & ~home_valid) | (pl_provided & ~pl_valid)

            return {"Episodes": episodes.index[error_mask].tolist()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        {
            "HOME_POST": [
                "AB1 0JD",
                "invalid",
                "AB1 0JD",
                "invalid",
                "AB10JD",
            ],
            "PL_POST": [
                "AB1 0JD",
                "AB1 0JD",
                "invalid",
                "invalid",
                "AB1 0JD",
            ],
        }
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1, 2, 3]}
