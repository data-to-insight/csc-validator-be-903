import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="118",
        description="Date of decision that a child should no longer be placed for adoption is before the current collection year or before the date the child started to be looked after.",
        affected_fields=["DECOM", "DECOM", "LS"],
    )

    def _validate(dfs):
        if ("PlacedAdoption" not in dfs) or ("Episodes" not in dfs):
            return {}
        else:
            placed_adoption = dfs["PlacedAdoption"]
            episodes = dfs["Episodes"]
            collection_start = dfs["metadata"]["collection_start"]
            code_list = ["V3", "V4"]

            # datetime
            episodes["DECOM"] = pd.to_datetime(
                episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
            )
            placed_adoption["DATE_PLACED_CEASED"] = pd.to_datetime(
                placed_adoption["DATE_PLACED_CEASED"],
                format="%d/%m/%Y",
                errors="coerce",
            )
            collection_start = pd.to_datetime(
                collection_start, format="%d/%m/%Y", errors="coerce"
            )

            # <DECOM> of the earliest episode with an <LS> not = 'V3' or 'V4'
            filter_by_ls = episodes[~(episodes["LS"].isin(code_list))]
            earliest_episode_idxs = filter_by_ls.groupby("CHILD")["DECOM"].idxmin()
            earliest_episodes = episodes[episodes.index.isin(earliest_episode_idxs)]

            # prepare to merge
            placed_adoption.reset_index(inplace=True)
            earliest_episodes.reset_index(inplace=True)

            # merge
            merged = earliest_episodes.merge(
                placed_adoption, on="CHILD", how="left", suffixes=["_eps", "_pa"]
            )

            # drop rows where DATE_PLACED_CEASED is not provided
            merged = merged.dropna(subset=["DATE_PLACED_CEASED"])
            # If provided <DATE_PLACED_CEASED> must not be prior to <COLLECTION_START_DATE> or <DECOM> of the earliest episode with an <LS> not = 'V3' or 'V4'
            mask = (merged["DATE_PLACED_CEASED"] < merged["DECOM"]) | (
                merged["DATE_PLACED_CEASED"] < collection_start
            )
            # error locations
            pa_error_locs = merged.loc[mask, "index_pa"]
            eps_error_locs = merged.loc[mask, "index_eps"]
            return {
                "Episodes": eps_error_locs.tolist(),
                "PlacedAdoption": pa_error_locs.unique().tolist(),
            }

    return error, _validate


# !# potential false negatives, as this only operates on current and previous year data


def test_validate():
    import pandas as pd

    fake_placed_adoption = pd.DataFrame(
        {
            "DATE_PLACED_CEASED": ["08/03/2020", "22/06/2020", "13/10/2022", pd.NA],
            "CHILD": ["101", "102", "103", "104"],
        }
    )
    fake_data_episodes = pd.DataFrame(
        [
            {
                "CHILD": "101",
                "LS": "L1",
                "DECOM": "01/01/2019",
            },  # 0 Fail DATE_PLACED_CEASED is before collection_start
            {
                "CHILD": "102",
                "LS": "V3",
                "DECOM": "01/01/2022",
            },  # 1 skip fail because LS is V3
            {"CHILD": "102", "LS": "X0", "DECOM": "20/12/2020"},  # 2 fail
            {"CHILD": "102", "LS": "L1", "DECOM": "03/01/2021"},  # 3
            {"CHILD": "102", "LS": "L1", "DECOM": "03/04/2022"},  # 4
            {"CHILD": "103", "LS": "X2", "DECOM": "01/01/2019"},  # 5 pass
            {
                "CHILD": "104",
                "LS": "L1",
                "DECOM": "01/01/2019",
            },  # 6 drop.na drops this child
        ]
    )
    metadata = {
        "collection_start": "01/04/2020",
    }
    fake_dfs = {
        "Episodes": fake_data_episodes,
        "PlacedAdoption": fake_placed_adoption,
        "metadata": metadata,
    }
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"Episodes": [0, 2], "PlacedAdoption": [0, 1]}
