import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="556",
        description="Date of decision that the child should be placed for adoption should be on or prior to the date that the freeing order was granted.",
        affected_fields=["DATE_PLACED", "DECOM"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs or "PlacedAdoption" not in dfs:
            return {}
        else:
            episodes = dfs["Episodes"]
            placedAdoptions = dfs["PlacedAdoption"]

            episodes["DECOM"] = pd.to_datetime(
                episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            placedAdoptions["DATE_PLACED"] = pd.to_datetime(
                placedAdoptions["DATE_PLACED"], format="%d/%m/%Y", errors="coerce"
            )

            episodes = episodes.reset_index()

            D1Episodes = episodes[episodes["LS"] == "D1"]

            merged = (
                D1Episodes.reset_index()
                .merge(
                    placedAdoptions,
                    how="left",
                    on="CHILD",
                )
                .set_index("index")
            )

            episodes_with_errors = merged[merged["DATE_PLACED"] > merged["DECOM"]]

            error_mask = episodes.index.isin(episodes_with_errors.index)

            error_locations = episodes.index[error_mask]

            return {"Episodes": error_locations.to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data_episodes = pd.DataFrame(
        {
            "CHILD": ["A", "B", "C"],
            "LS": ["C1", "D1", "D1"],
            "DECOM": [pd.NA, "15/03/2020", "15/03/2020"],
        }
    )
    fake_data_placed_adoption = pd.DataFrame(
        {
            "CHILD": ["A", "B", "C"],
            "DATE_PLACED": [pd.NA, "15/04/2020", "15/02/2020"],
        }
    )

    fake_dfs = {
        "Episodes": fake_data_episodes,
        "PlacedAdoption": fake_data_placed_adoption,
    }

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1]}
