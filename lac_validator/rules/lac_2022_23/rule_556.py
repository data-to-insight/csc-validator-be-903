import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="556",
    message="Date of decision that the child should be placed for adoption should be on or prior to the date that the freeing order was granted.",
    affected_fields=["DATE_PLACED", "DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs or "PlacedAdoption" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        placedAdoptions = dfs["PlacedAdoption"]

        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        placedAdoptions["DATEPLACED"] = pd.todatetime(
            placedAdoptions["DATEPLACED"], format="%d/%m/%Y", errors="coerce"
        )

        episodes = episodes.resetindex()

        D1Episodes = episodes[episodes["LS"] == "D1"]

        merged = (
            D1Episodes.resetindex()
            .merge(
                placedAdoptions,
                how="left",
                on="CHILD",
            )
            .setindex("index")
        )

        episodeswitherrors = merged[merged["DATEPLACED"] > merged["DECOM"]]

        errormask = episodes.index.isin(episodeswitherrors.index)

        errorlocations = episodes.index[errormask]

        return {"Episodes": errorlocations.tolist()}


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
