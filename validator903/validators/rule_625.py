import pandas as pd

from validator903.types import ErrorDefinition


def validate():
    error = ErrorDefinition(
        code="625",
        description="Date of birth of the first child is beyond the end of this reporting year or the date the child ceased to be looked after.",
        affected_fields=["MC_DOB", "DEC"],
    )

    def _validate(dfs):
        if "Episodes" not in dfs or "Header" not in dfs:
            return {}
        else:
            episodes = dfs["Episodes"]
            header = dfs["Header"]
            collection_end = dfs["metadata"]["collection_end"]

            # datetime conversion
            collection_end = pd.to_datetime(
                collection_end, format="%d/%m/%Y", errors="coerce"
            )
            header["MC_DOB"] = pd.to_datetime(
                header["MC_DOB"], format="%d/%m/%Y", errors="coerce"
            )
            episodes["DEC"] = pd.to_datetime(
                episodes["DEC"], format="%d/%m/%Y", errors="coerce"
            )
            # prepare to merge
            header.reset_index(inplace=True)
            episodes.reset_index(inplace=True)
            # latest episodes
            eps_last_indices = episodes.groupby("CHILD")["DEC"].idxmax()
            latest_episodes = episodes[episodes.index.isin(eps_last_indices)]
            merged = latest_episodes.merge(
                header, on="CHILD", how="left", suffixes=["_eps", "_er"]
            )
            # If provided <MC_DOB> must not be > <COLLECTION_END> or <DEC> of latest episode
            mask = (merged["MC_DOB"] > collection_end) | (
                merged["MC_DOB"] > merged["DEC"]
            )
            header_error_locs = merged.loc[mask, "index_er"]
            eps_error_locs = merged.loc[mask, "index_eps"]
            return {
                "Header": header_error_locs.unique().tolist(),
                "Episodes": eps_error_locs.tolist(),
            }

    return error, _validate


# !# big potential false positives, as this only operates on the current and previous year data
# should use collection start/end & DOB to exclude children whose first/last episode dates mean we probably can't tell


def test_validate():
    import pandas as pd

    fake_data_header = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103"],
            "MC_DOB": ["01/11/2021", "19/12/2016", pd.NA],
            # 0 MC_DOB > collection_end FAIL
            # 1 MC_DOB < collection_end but > DEC of latest episode FAIL
            # 2 MC_DOB not provided IGNORE
        }
    )
    fake_data_episodes = pd.DataFrame(
        {
            "CHILD": ["101", "101", "102", "102", "103", "103", "103"],
            "DEC": [
                "02/12/2021",
                "11/11/2012",
                "03/10/2014",
                "11/11/2015",
                "01/01/2020",
                "11/11/2020",
                "01/02/2020",
            ],
        }
    )
    metadata = {"collection_end": "31/03/2021"}
    fake_dfs = {
        "metadata": metadata,
        "Episodes": fake_data_episodes,
        "Header": fake_data_header,
    }
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"Episodes": [0, 3], "Header": [0, 1]}
