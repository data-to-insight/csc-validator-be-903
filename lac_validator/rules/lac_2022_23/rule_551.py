from validator903.types import ErrorDefinition


@rule_definition(
    code="551",
    message="Child has been placed for adoption but there is no date of the decision that the child should be placed for adoption.",
    affected_fields=["DATE_PLACED", "PLACE"],
)
def validate(dfs):
    if "Episodes" not in dfs or "PlacedAdoption" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        placedAdoptions = dfs["PlacedAdoption"]

        episodes = episodes.resetindex()

        placecodes = ["A3", "A4", "A5", "A6"]

        placeEpisodes = episodes[episodes["PLACE"].isin(placecodes)]

        merged = placeEpisodes.merge(placedAdoptions, how="left", on="CHILD").setindex(
            "index"
        )

        episodeswitherrors = merged[merged["DATEPLACED"].isna()]

        errormask = episodes.index.isin(episodeswitherrors.index)

        errorlocations = episodes.index[errormask]

        return {"Episodes": errorlocations.tolist()}


def test_validate():
    import pandas as pd

    fake_data_episodes = pd.DataFrame(
        {
            "CHILD": ["0", "A", "B", "C", "D", "E", "F", "G", "H", "I"],
            "PLACE": ["x", "A3", "A4", "A5", "A6", "A3", "A4", "x", "A3", "A5"],
        }
    )
    fake_data_placed_adoption = pd.DataFrame(
        {
            "CHILD": ["A", "B", "C", "D", "E", "F", "G", "H"],
            "DATE_PLACED": [
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

    assert result == {"Episodes": [1, 2, 3, 4, 9]}
