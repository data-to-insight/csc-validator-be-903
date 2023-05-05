import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="607",
    message="Child ceased to be looked after in the year, but mother field has not been completed.",
    affected_fields=["DEC", "REC", "MOTHER", "LS", "SEX"],
)
def validate(dfs):
    if "Header" not in dfs or "Episodes" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        episodes = dfs["Episodes"]
        collectionstart = dfs["metadata"]["collectionstart"]
        collectionend = dfs["metadata"]["collectionend"]
        codelist = ["V3", "V4"]

        # convert to datetiime format
        episodes["DEC"] = pd.todatetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )
        collectionstart = pd.todatetime(
            collectionstart, format="%d/%m/%Y", errors="coerce"
        )
        collectionend = pd.todatetime(collectionend, format="%d/%m/%Y", errors="coerce")

        # prepare to merge
        episodes.resetindex(inplace=True)
        header.resetindex(inplace=True)

        merged = episodes.merge(header, on="CHILD", how="left", suffixes=["eps", "er"])

        # CEASEDTOBELOOKEDAFTER = DEC is not null and REC is filled but not equal to X1
        CEASEDTOBELOOKEDAFTER = merged["DEC"].notna() & (
            (merged["REC"] != "X1") & merged["REC"].notna()
        )
        # and <LS> not = ‘V3’ or ‘V4’
        checkLS = ~(merged["LS"].isin(codelist))
        # and <DEC> is in <CURRENTCOLLECTIONYEAR
        checkDEC = (collectionstart <= merged["DEC"]) & (merged["DEC"] <= collectionend)
        # Where <CEASEDTOBELOOKEDAFTER> = ‘Y’, and <LS> not = ‘V3’ or ‘V4’ and <DEC> is in <CURRENTCOLLECTIONYEAR> and <SEX> = ‘2’ then <MOTHER> should be provided.
        mask = (
            CEASEDTOBELOOKEDAFTER
            & checkLS
            & checkDEC
            & (merged["SEX"] == "2")
            & (merged["MOTHER"].isna())
        )
        headererrorlocs = merged.loc[mask, "indexer"]
        epserrorlocs = merged.loc[mask, "indexeps"]
        return {
            "Episodes": epserrorlocs.tolist(),
            "Header": headererrorlocs.unique().tolist(),
        }


def test_validate():
    import pandas as pd

    fake_data_eps = pd.DataFrame(
        [
            {
                "CHILD": 101,
                "DEC": "01/01/2021",
                "REC": pd.NA,
                "LS": "L1",
            },  # 0 Ignore: REC is null
            {
                "CHILD": 102,
                "DEC": "01/01/2001",
                "REC": "A3",
                "LS": "V4",
            },  # 1 Ignore: LS is V4
            {
                "CHILD": 103,
                "DEC": "20/12/2001",
                "REC": "E15",
                "LS": "V3",
            },  # 2 Ignore: LS is V3
            {
                "CHILD": 104,
                "DEC": "03/01/2020",
                "REC": "E46",
                "LS": "L4",
            },  # 3 Ignore: DEC out of range
            {
                "CHILD": 105,
                "DEC": "03/04/2020",
                "REC": "E48",
                "LS": "L1",
            },  # 4 FAIL
            {
                "CHILD": 105,
                "DEC": "01/07/2020",
                "REC": "X2",
                "LS": "XO",
            },  # 5 FAIL
            {
                "CHILD": 105,
                "DEC": "10/01/2021",
                "REC": "E11",
                "LS": "L4",
            },  # 6 FAIL
            {
                "CHILD": 108,
                "DEC": "11/02/2021",
                "REC": "E48",
                "LS": "L1",
            },  # 7
            {
                "CHILD": 109,
                "DEC": "25/01/2002",
                "REC": "X1",
                "LS": "XO",
            },  # 8 Ignore: REC is X1
            {
                "CHILD": 110,
                "DEC": "25/01/2021",
                "REC": "E47",
                "LS": pd.NA,
            },  # 9
            {
                "CHILD": 111,
                "DEC": pd.NA,
                "REC": "E45",
                "LS": "L4",
            },  # 10 Ignore : DEC is null
            {
                "CHILD": 112,
                "DEC": "25/08/2020",
                "REC": "E46",
                "LS": "XO",
            },  # 11
        ]
    )
    fake_data_header = pd.DataFrame(
        [
            {"CHILD": 101, "SEX": "2", "MOTHER": pd.NA},  # 0 FAIL Ignore: REC is null
            {"CHILD": 102, "SEX": "2", "MOTHER": "0"},  # 1 Ignore: LS is V4
            {"CHILD": 103, "SEX": "2", "MOTHER": pd.NA},  # 2 Ignore: LS is V3
            {"CHILD": 104, "SEX": "2", "MOTHER": pd.NA},  # 3 Ignore: DEC out of range
            {"CHILD": 105, "SEX": "2", "MOTHER": pd.NA},  # 4 FAIL
            {"CHILD": 108, "SEX": "1", "MOTHER": pd.NA},  # 5
            {"CHILD": 109, "SEX": "2", "MOTHER": "0"},  # 6 Ignore: REC is X1
            {"CHILD": 110, "SEX": "2", "MOTHER": pd.NA},  # 7 FAIL
            {"CHILD": 111, "SEX": "2", "MOTHER": "0"},  # 8 Ignore : DEC is null
            {"CHILD": 112, "SEX": "2", "MOTHER": "1"},  # 9
        ]
    )
    metadata = {"collection_start": "01/04/2020", "collection_end": "31/03/2021"}
    fake_dfs = {
        "Header": fake_data_header,
        "Episodes": fake_data_eps,
        "metadata": metadata,
    }
    error_defn, error_func = validate()
    result = error_func(fake_dfs)
    assert result == {"Header": [4, 7], "Episodes": [4, 5, 6, 9]}
