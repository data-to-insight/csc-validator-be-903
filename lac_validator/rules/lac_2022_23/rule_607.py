import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


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
        collection_start = dfs["metadata"]["collection_start"]
        collection_end = dfs["metadata"]["collection_end"]
        code_list = ["V3", "V4"]

        # convert to datetiime format
        episodes["DEC"] = pd.to_datetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )
        collection_start = pd.to_datetime(
            collection_start, format="%d/%m/%Y", errors="coerce"
        )
        collection_end = pd.to_datetime(
            collection_end, format="%d/%m/%Y", errors="coerce"
        )

        # prepare to merge
        episodes.reset_index(inplace=True)
        header.reset_index(inplace=True)

        merged = episodes.merge(
            header, on="CHILD", how="left", suffixes=["_eps", "_er"]
        )

        # CEASED_TO_BE_LOOKED_AFTER = DEC is not null and REC is filled but not equal to X1
        CEASED_TO_BE_LOOKED_AFTER = merged["DEC"].notna() & (
            (merged["REC"] != "X1") & merged["REC"].notna()
        )
        # and <LS> not = ‘V3’ or ‘V4’
        check_LS = ~(merged["LS"].isin(code_list))
        # and <DEC> is in <CURRENT_COLLECTION_YEAR
        check_DEC = (collection_start <= merged["DEC"]) & (
            merged["DEC"] <= collection_end
        )
        # Where <CEASED_TO_BE_LOOKED_AFTER> = ‘Y’, and <LS> not = ‘V3’ or ‘V4’ and <DEC> is in <CURRENT_COLLECTION_YEAR> and <SEX> = ‘2’ then <MOTHER> should be provided.
        mask = (
            CEASED_TO_BE_LOOKED_AFTER
            & check_LS
            & check_DEC
            & (merged["SEX"] == "2")
            & (merged["MOTHER"].isna())
        )
        header_error_locs = merged.loc[mask, "index_er"]
        eps_error_locs = merged.loc[mask, "index_eps"]
        return {
            "Episodes": eps_error_locs.tolist(),
            "Header": header_error_locs.unique().tolist(),
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
