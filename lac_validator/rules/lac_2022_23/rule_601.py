import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="601",
    message="The additional fields relating to adoption have not been completed although the episode data shows that the child was adopted during the year.",
    affected_fields=[
        "REC",
        "DATE_INT",
        "DATE_MATCH",
        "FOSTER_CARE",
        "NB_ADOPTR",
        "SEX_ADOPTR",
        "LS_ADOPTR",
    ],
)
def validate(dfs):
    if "Episodes" not in dfs or "AD1" not in dfs:
        return {}
    else:
        ad1 = dfs["AD1"]
        episodes = dfs["Episodes"]
        collectionstart = dfs["metadata"]["collectionstart"]
        collectionend = dfs["metadata"]["collectionend"]

        # prepare to merge
        ad1.resetindex(inplace=True)
        episodes.resetindex(inplace=True)

        collectionstart = pd.todatetime(
            collectionstart, format="%d/%m/%Y", errors="coerce"
        )
        collectionend = pd.todatetime(collectionend, format="%d/%m/%Y", errors="coerce")
        episodes["DEC"] = pd.todatetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )

        # only keep episodes with adoption RECs during year
        adoptionepsmask = (
            (episodes["DEC"] >= collectionstart)
            & (episodes["DEC"] <= collectionend)
            & episodes["REC"].isin(["E11", "E12"])
        )
        episodes = episodes[adoptionepsmask]

        # inner merge to take only episodes of children which are also found in the ad1 table
        merged = episodes.merge(ad1, on="CHILD", how="inner", suffixes=["eps", "ad1"])

        someabsent = (
            merged[
                [
                    "DATEINT",
                    "DATEMATCH",
                    "FOSTERCARE",
                    "NBADOPTR",
                    "SEXADOPTR",
                    "LSADOPTR",
                ]
            ]
            .isna()
            .any(axis=1)
        )

        errorlocsad1 = merged.loc[someabsent, "indexad1"].unique().tolist()
        errorlocseps = merged.loc[someabsent, "indexeps"].unique().tolist()

        return {"AD1": errorlocsad1, "Episodes": errorlocseps}


def test_validate():
    import pandas as pd

    fake_data_episodes = pd.DataFrame(
        [
            {
                "CHILD": "101",
                "DEC": "01/01/2009",
                "REC": "E45",
                "DECOM": "01/01/2009",
            },  # 0
            {
                "CHILD": "102",
                "DEC": "01/01/2021",
                "REC": "E11",
                "DECOM": "01/01/2001",
            },  # 1 fail
            {
                "CHILD": "102",
                "DEC": "20/12/2021",
                "REC": "E15",
                "DECOM": "20/12/2001",
            },  # 2
            {
                "CHILD": "102",
                "DEC": "03/07/2020",
                "REC": "E12",
                "DECOM": "03/01/2019",
            },  # 3 fail
            {
                "CHILD": "102",
                "DEC": "03/04/2019",
                "REC": "E48",
                "DECOM": "03/04/2008",
            },  # 4
            {
                "CHILD": "103",
                "DEC": "26/05/2020",
                "REC": "E12",
                "DECOM": "01/01/2002",
            },  # 5 pass
            {
                "CHILD": "104",
                "DEC": "10/01/2002",
                "REC": "E11",
                "DECOM": "10/01/2002",
            },  # 6
            {
                "CHILD": "104",
                "DEC": "11/02/2010",
                "REC": "X1",
                "DECOM": "11/02/2010",
            },  # 7
            {
                "CHILD": "104",
                "DEC": "25/01/2002",
                "REC": "X1",
                "DECOM": "25/01/2002",
            },  # 8
            {
                "CHILD": "105",
                "DEC": "25/01/2002",
                "REC": "E47",
                "DECOM": "25/01/2002",
            },  # 9
            {"CHILD": "105", "DEC": pd.NA, "REC": "E45", "DECOM": pd.NA},  # 10
        ]
    )
    fake_data_ad1 = pd.DataFrame(
        {
            "CHILD": ["101", "102", "103", "104", "105"],
            "DATE_INT": [pd.NA, pd.NA, "XXX", pd.NA, "XXX"],
            "DATE_MATCH": [pd.NA, "XXX", "XXX", pd.NA, "XXX"],
            "FOSTER_CARE": [pd.NA, pd.NA, "XXX", pd.NA, "XXX"],
            "NB_ADOPTR": [pd.NA, pd.NA, "XXX", pd.NA, "XXX"],
            "SEX_ADOPTR": [pd.NA, pd.NA, "XXX", pd.NA, "XXX"],
            "LS_ADOPTR": [pd.NA, pd.NA, "XXX", "XXX", "XXX"],
        }
    )
    metadata = {"collection_start": "01/04/2020", "collection_end": "31/03/2021"}
    fake_dfs = {
        "Episodes": fake_data_episodes,
        "AD1": fake_data_ad1,
        "metadata": metadata,
    }
    error_defn, error_func = validate()
    result = error_func(fake_dfs)

    assert result == {
        "AD1": [
            1,
        ],
        "Episodes": [1, 3],
    }
