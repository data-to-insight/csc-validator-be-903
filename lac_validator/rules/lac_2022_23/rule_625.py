import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="625",
    message="Date of birth of the first child is beyond the end of this reporting year or the date the child ceased to be looked after.",
    affected_fields=["MC_DOB", "DEC"],
)
def validate(dfs):
    if "Episodes" not in dfs or "Header" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        header = dfs["Header"]
        collectionend = dfs["metadata"]["collectionend"]

        # datetime conversion
        collectionend = pd.todatetime(collectionend, format="%d/%m/%Y", errors="coerce")
        header["MCDOB"] = pd.todatetime(
            header["MCDOB"], format="%d/%m/%Y", errors="coerce"
        )
        episodes["DEC"] = pd.todatetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )
        # prepare to merge
        header.resetindex(inplace=True)
        episodes.resetindex(inplace=True)
        # latest episodes
        epslastindices = episodes.groupby("CHILD")["DEC"].idxmax()
        latestepisodes = episodes[episodes.index.isin(epslastindices)]
        merged = latestepisodes.merge(
            header, on="CHILD", how="left", suffixes=["eps", "er"]
        )
        # If provided <MCDOB> must not be > <COLLECTIONEND> or <DEC> of latest episode
        mask = (merged["MCDOB"] > collectionend) | (merged["MCDOB"] > merged["DEC"])
        headererrorlocs = merged.loc[mask, "indexer"]
        epserrorlocs = merged.loc[mask, "indexeps"]
        return {
            "Header": headererrorlocs.unique().tolist(),
            "Episodes": epserrorlocs.tolist(),
        }


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
