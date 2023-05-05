import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="118",
    message="Date of decision that a child should no longer be placed for adoption is before the current collection year or before the date the child started to be looked after.",
    affected_fields=["DECOM", "DECOM", "LS"],
)
def validate(dfs):
    if ("PlacedAdoption" not in dfs) or ("Episodes" not in dfs):
        return {}
    else:
        placedadoption = dfs["PlacedAdoption"]
        episodes = dfs["Episodes"]
        collectionstart = dfs["metadata"]["collectionstart"]
        codelist = ["V3", "V4"]

        # datetime
        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        placedadoption["DATEPLACEDCEASED"] = pd.todatetime(
            placedadoption["DATEPLACEDCEASED"],
            format="%d/%m/%Y",
            errors="coerce",
        )
        collectionstart = pd.todatetime(
            collectionstart, format="%d/%m/%Y", errors="coerce"
        )

        # <DECOM> of the earliest episode with an <LS> not = 'V3' or 'V4'
        filterbyls = episodes[~(episodes["LS"].isin(codelist))]
        earliestepisodeidxs = filterbyls.groupby("CHILD")["DECOM"].idxmin()
        earliestepisodes = episodes[episodes.index.isin(earliestepisodeidxs)]

        # prepare to merge
        placedadoption.resetindex(inplace=True)
        earliestepisodes.resetindex(inplace=True)

        # merge
        merged = earliestepisodes.merge(
            placedadoption, on="CHILD", how="left", suffixes=["eps", "pa"]
        )

        # drop rows where DATEPLACEDCEASED is not provided
        merged = merged.dropna(subset=["DATEPLACEDCEASED"])
        # If provided <DATEPLACEDCEASED> must not be prior to <COLLECTIONSTARTDATE> or <DECOM> of the earliest episode with an <LS> not = 'V3' or 'V4'
        mask = (merged["DATEPLACEDCEASED"] < merged["DECOM"]) | (
            merged["DATEPLACEDCEASED"] < collectionstart
        )
        # error locations
        paerrorlocs = merged.loc[mask, "indexpa"]
        epserrorlocs = merged.loc[mask, "indexeps"]
        return {
            "Episodes": epserrorlocs.tolist(),
            "PlacedAdoption": paerrorlocs.unique().tolist(),
        }


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
