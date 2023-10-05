import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="558",
    message="If a child has been adopted, then the decision to place them for adoption has not been disrupted and the date of the decision that a child should no longer be placed for adoption should be left blank.",
    affected_fields=["DATE_PLACED_CEASED", "REC"],
)
def validate(dfs):
    if "Episodes" not in dfs or "PlacedAdoption" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        placedAdoptions = dfs["PlacedAdoption"]

        episodes = episodes.reset_index()

        rec_codes = ["E11", "E12"]

        placeEpisodes = episodes[episodes["REC"].isin(rec_codes)]

        merged = placeEpisodes.merge(placedAdoptions, how="left", on="CHILD").set_index(
            "index"
        )

        # Add's a year column for grouping by year later.
        merged["YEAR"] = pd.DatetimeIndex(
            merged["DATE_PLACED_CEASED"], dayfirst=True
        ).year

        # List of children who have null dates to be excluded (assumes the null is their most recent)
        children_with_null = merged[(merged["DATE_PLACED_CEASED"].isna())][
            "CHILD"
        ].tolist()

        episodes_not_null = merged[~(merged["CHILD"].isin(children_with_null))]

        episodes_not_null["COUNT"] = episodes_not_null.groupby(
            ["CHILD", "YEAR"], group_keys=False
        )["DATE_PLACED_CEASED"].transform("count")

        episodes_with_errors = episodes_not_null[episodes_not_null["COUNT"] > 1]

        error_mask = episodes.index.isin(episodes_with_errors.index)

        error_locations = episodes.index[error_mask]

        return {"Episodes": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data_episodes = pd.DataFrame(
        {
            "CHILD": [
                "0",
                "A",
                "B",
                "C",
                "D",
                "E",
                "F",
                "G",
                "H",
                "I",
            ],
            "REC": [
                "x",
                "E11",
                "E12",
                "E11",
                "E12",
                "E11",
                "E12",
                "E11",
                "E11",
                "E12",
            ],
        }
    )
    fake_data_placed_adoption = pd.DataFrame(
        {
            "CHILD": ["A", "B", "C", "D", "E", "F", "G", "H", "D", "E", "I", "I", "I"],
            "DATE_PLACED_CEASED": [
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                "01/01/2020",
                "01/01/2020",
                "15/04/2020",
                pd.NA,
                "28th Jan 1930",
                "02/01/2020",
                "01/01/1930",
                "01/01/1930",
                "02/01/1930",
                pd.NA,
            ],
        }
    )

    fake_dfs = {
        "Episodes": fake_data_episodes,
        "PlacedAdoption": fake_data_placed_adoption,
    }

    result = validate(fake_dfs)

    assert result == {"Episodes": [4]}
