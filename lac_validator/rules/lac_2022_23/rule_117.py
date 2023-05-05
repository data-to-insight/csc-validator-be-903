import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="117",
    message="Date of decision that a child should/should no longer be placed for adoption is beyond the current collection year or after the child ceased to be looked after.",
    affected_fields=["DATE_PLACED_CEASED", "DATE_PLACED", "DEC", "REC", "DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs or "PlacedAdoption" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        placedadoption = dfs["PlacedAdoption"]
        collectionend = dfs["metadata"]["collectionend"]

        # datetime
        placedadoption["DATEPLACEDCEASED"] = pd.todatetime(
            placedadoption["DATEPLACEDCEASED"],
            format="%d/%m/%Y",
            errors="coerce",
        )
        placedadoption["DATEPLACED"] = pd.todatetime(
            placedadoption["DATEPLACED"], format="%d/%m/%Y", errors="coerce"
        )
        collectionend = pd.todatetime(collectionend, format="%d/%m/%Y", errors="coerce")
        episodes["DEC"] = pd.todatetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )
        episodes["DECOM"] = pd.todatetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )

        # Drop nans and continuing episodes
        episodes = episodes.dropna(subset=["DECOM"])
        episodes = episodes[episodes["REC"] != "X1"]

        episodes = episodes.loc[episodes.groupby("CHILD")["DECOM"].idxmax()]

        # prepare to merge
        placedadoption.resetindex(inplace=True)
        episodes.resetindex(inplace=True)

        p4acols = ["DATEPLACED", "DATEPLACEDCEASED"]

        # latest episodes
        merged = episodes.merge(
            placedadoption, on="CHILD", how="left", suffixes=["eps", "pa"]
        )
        mask = (
            (merged["DATEPLACED"] > collectionend)
            | (merged["DATEPLACED"] > merged["DEC"])
            | (merged["DATEPLACEDCEASED"] > collectionend)
            | (merged["DATEPLACEDCEASED"] > merged["DEC"])
        )
        # If provided <DATEPLACED> and/or <DATEPLACEDCEASED> must not be > <COLLECTIONENDDATE> or <DEC> of latest episode where <REC> not = 'X1'
        paerrorlocs = merged.loc[mask, "indexpa"]
        epserrorlocs = merged.loc[mask, "indexeps"]
        return {
            "Episodes": epserrorlocs.tolist(),
            "PlacedAdoption": paerrorlocs.unique().tolist(),
        }


def test_validate():
    import pandas as pd

    metadata = {"collection_end": "31/03/2018"}
    fake_placed_adoption = pd.DataFrame(
        [
            {
                "CHILD": 101,
                "DATE_PLACED_CEASED": "26/05/2000",
                "DATE_PLACED": "26/05/2000",
            },  # 0
            {
                "CHILD": 102,
                "DATE_PLACED_CEASED": "01/07/2018",
                "DATE_PLACED": "26/05/2000",
            },
            # 1 Fail DATE_PLACED_CEASED > collection_end
            {
                "CHILD": 103,
                "DATE_PLACED_CEASED": "26/05/2000",
                "DATE_PLACED": pd.NA,
            },  # 2
            {
                "CHILD": 104,
                "DATE_PLACED_CEASED": "26/05/2017",
                "DATE_PLACED": "01/02/2016",
            },
            # 3 Fail greater than DEC of latest episode
            {
                "CHILD": 105,
                "DATE_PLACED_CEASED": pd.NA,
                "DATE_PLACED": "26/05/2019",
            },  # 4 Fail DATE_PLACED > collection_end
        ]
    )
    fake_data_eps = pd.DataFrame(
        [
            {
                "CHILD": 101,
                "DEC": "01/01/2009",
                "REC": "E45",
                "DECOM": "01/01/2009",
            },  # 0
            {
                "CHILD": 102,
                "DEC": "01/01/2001",
                "REC": "A3",
                "DECOM": "01/01/2001",
            },  # 1
            {
                "CHILD": 102,
                "DEC": "20/12/2001",
                "REC": "E15",
                "DECOM": "20/12/2001",
            },  # 2
            {
                "CHILD": 102,
                "DEC": "03/01/2019",
                "REC": "E46",
                "DECOM": "03/01/2019",
            },  # 3 Fail
            {
                "CHILD": 102,
                "DEC": "03/04/2008",
                "REC": "E48",
                "DECOM": "03/04/2008",
            },  # 4
            {
                "CHILD": 103,
                "DEC": "01/01/2002",
                "REC": "X2",
                "DECOM": "01/01/2002",
            },  # 5
            {
                "CHILD": 104,
                "DEC": "10/01/2002",
                "REC": "E11",
                "DECOM": "10/01/2002",
            },  # 6
            {
                "CHILD": 104,
                "DEC": "11/02/2010",
                "REC": "X1",
                "DECOM": "11/02/2010",
            },  # 7 Fail Ignored
            {
                "CHILD": 104,
                "DEC": "25/01/2002",
                "REC": "X1",
                "DECOM": "25/01/2002",
            },  # 8 Ignored REC is X1
            {
                "CHILD": 105,
                "DEC": "25/01/2002",
                "REC": "E47",
                "DECOM": "25/01/2002",
            },  # 9
            {"CHILD": 105, "DEC": pd.NA, "REC": "E45", "DECOM": pd.NA},  # 10
        ]
    )
    # TODO: in  the scenario where the REC of the latest episodes is X1, should the episode before the lastest
    #  be considered instead?. This will entail filtering by X1 before doing idxmax. Is this what this rule means?.

    fake_dfs = {
        "Episodes": fake_data_eps,
        "metadata": metadata,
        "PlacedAdoption": fake_placed_adoption,
    }
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"Episodes": [3, 6, 9], "PlacedAdoption": [1, 3, 4]}
