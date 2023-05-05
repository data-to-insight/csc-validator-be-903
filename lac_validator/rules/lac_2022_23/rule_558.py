from validator903.types import ErrorDefinition


@rule_definition(
    code="558",
    message="If a child has been adopted, then the decision to place them for adoption has not been disrupted and the date of the decision that a child should no longer be placed for adoption should be left blank. if the REC code is either E11 or E12 then the DATE PLACED CEASED date should not be provided",
    affected_fields=["DATE_PLACED_CEASED", "REC"],
)
def validate(dfs):
    if "Episodes" not in dfs or "PlacedAdoption" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        placedAdoptions = dfs["PlacedAdoption"]

        episodes = episodes.resetindex()

        reccodes = ["E11", "E12"]

        placeEpisodes = episodes[episodes["REC"].isin(reccodes)]

        merged = placeEpisodes.merge(placedAdoptions, how="left", on="CHILD").setindex(
            "index"
        )

        episodeswitherrors = merged[merged["DATEPLACEDCEASED"].notna()]

        errormask = episodes.index.isin(episodeswitherrors.index)

        errorlocations = episodes.index[errormask]

        return {"Episodes": errorlocations.tolist()}


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
