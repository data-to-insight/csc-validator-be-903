from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="558",
        description="If a child has been adopted, then the decision to place them for adoption has not been disrupted and the date of the decision that a child should no longer be placed for adoption should be left blank. if the REC code is either E11 or E12 then the DATE PLACED CEASED date should not be provided",
        affected_fields=["DATE_PLACED_CEASED", "REC"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs or "PlacedAdoption" not in dfs:
            return {}
        else:
            episodes = dfs["Episodes"]
            placedAdoptions = dfs["PlacedAdoption"]

            episodes = episodes.reset_index()

            rec_codes = ["E11", "E12"]

            placeEpisodes = episodes[episodes["REC"].isin(rec_codes)]

            merged = placeEpisodes.merge(
                placedAdoptions, how="left", on="CHILD"
            ).set_index("index")

            episodes_with_errors = merged[merged["DATE_PLACED_CEASED"].notna()]

            error_mask = episodes.index.isin(episodes_with_errors.index)

            error_locations = episodes.index[error_mask]

            return {"Episodes": error_locations.to_list()}

    return error, _validate


def test_validate():
    import pandas as pd

    fake_data_episodes = pd.DataFrame(
        {
            "CHILD": ["0", "A", "B", "C", "D", "E", "F", "G", "H", "I"],
            "REC": ["x", "E11", "E12", "E11", "E12", "E11", "E12", "E11", "E11", "A3"],
        }
    )
    fake_data_placed_adoption = pd.DataFrame(
        {
            "CHILD": ["A", "B", "C", "D", "E", "F", "G", "H"],
            "DATE_PLACED_CEASED": [
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                "01/01/2020",
                "15/04/2020",
                pd.NA,
                "28th Jan 1930",
            ],
        }
    )

    fake_dfs = {
        "Episodes": fake_data_episodes,
        "PlacedAdoption": fake_data_placed_adoption,
    }

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [5, 6, 8]}
