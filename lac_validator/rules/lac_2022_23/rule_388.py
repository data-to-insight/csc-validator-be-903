import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="388",
    message="Reason episode ceased is coded new episode begins, but there is no continuation episode.",
    affected_fields=["REC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        df = dfs["Episodes"]
        df["DECOM"] = pd.to_datetime(df["DECOM"], format="%d/%m/%Y", errors="coerce")
        df["DEC"] = pd.to_datetime(df["DEC"], format="%d/%m/%Y", errors="coerce")

        df["DECOM"] = df["DECOM"].fillna(
            "01/01/1901"
        )  # Watch for potential future issues
        df = df.sort_values(["CHILD", "DECOM"])

        df["DECOM_NEXT_EPISODE"] = df.groupby(["CHILD"])["DECOM"].shift(-1)

        # The max DECOM for each child is also the one with no next episode
        # And we also add the skipna option
        # grouped_decom_by_child = df.groupby(['CHILD'])['DECOM'].idxmax(skipna=True)
        no_next = df.DECOM_NEXT_EPISODE.isna() & df.CHILD.notna()

        # Dataframe with the maximum DECOM removed
        max_decom_removed = df[~no_next]
        # Dataframe with the maximum DECOM only
        max_decom_only = df[no_next]

        # Case 1: If reason episode ceased is coded X1 there must be a subsequent episode
        #        starting on the same day.
        case1 = max_decom_removed[
            (max_decom_removed["REC"] == "X1")
            & (max_decom_removed["DEC"].notna())
            & (max_decom_removed["DECOM_NEXT_EPISODE"].notna())
            & (max_decom_removed["DEC"] != max_decom_removed["DECOM_NEXT_EPISODE"])
        ]

        # Case 2: If an episode ends but the child continues to be looked after, a new
        #        episode should start on the same day.The reason episode ceased code of
        #        the episode which ends must be X1.
        case2 = max_decom_removed[
            (max_decom_removed["REC"] != "X1")
            & (max_decom_removed["REC"].notna())
            & (max_decom_removed["DEC"].notna())
            & (max_decom_removed["DECOM_NEXT_EPISODE"].notna())
            & (max_decom_removed["DEC"] == max_decom_removed["DECOM_NEXT_EPISODE"])
        ]

        # Case 3: If a child ceases to be looked after reason episode ceased code X1 must
        #        not be used.
        case3 = max_decom_only[
            (max_decom_only["DEC"].notna()) & (max_decom_only["REC"] == "X1")
        ]

        mask_case1 = case1.index.tolist()
        mask_case2 = case2.index.tolist()
        mask_case3 = case3.index.tolist()

        mask = mask_case1 + mask_case2 + mask_case3

        mask.sort()
        return {"Episodes": mask}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DECOM": "01/06/2020",
                "DEC": "04/06/2020",
                "REC": "X1",
            },  # 0  Fails Case 1
            {
                "CHILD": "111",
                "DECOM": "05/06/2020",
                "DEC": "06/06/2020",
                "REC": "X1",
            },  # 1
            {
                "CHILD": "111",
                "DECOM": "06/06/2020",
                "DEC": "08/06/2020",
                "REC": "X1",
            },  # 2
            {
                "CHILD": "111",
                "DECOM": "08/06/2020",
                "DEC": "05/06/2020",
                "REC": "X1",
            },  # 3  Fails Case 3
            {
                "CHILD": "222",
                "DECOM": "05/06/2020",
                "DEC": "06/06/2020",
                "REC": pd.NA,
            },  # 4
            {
                "CHILD": "333",
                "DECOM": "06/06/2020",
                "DEC": "07/06/2020",
                "REC": "E11",
            },  # 5  Fails Case 2
            {"CHILD": "333", "DECOM": "07/06/2020", "DEC": pd.NA, "REC": pd.NA},  # 6
            {
                "CHILD": "444",
                "DECOM": "08/06/2020",
                "DEC": "09/06/2020",
                "REC": "X1",
            },  # 7
            {
                "CHILD": "444",
                "DECOM": "09/06/2020",
                "DEC": "10/06/2020",
                "REC": "E11",
            },  # 8
            {"CHILD": "444", "DECOM": "15/06/2020", "DEC": pd.NA, "REC": pd.NA},  # 9
            {
                "CHILD": "555",
                "DECOM": "11/06/2020",
                "DEC": "12/06/2020",
                "REC": "X1",
            },  # 10  Fails Case 3
            {
                "CHILD": "6666",
                "DECOM": "12/06/2020",
                "DEC": "13/06/2020",
                "REC": "X1",
            },  # 11
            {
                "CHILD": "6666",
                "DECOM": "13/06/2020",
                "DEC": "14/06/2020",
                "REC": "X1",
            },  # 12
            {
                "CHILD": "6666",
                "DECOM": "14/06/2020",
                "DEC": "15/06/2020",
                "REC": "X1",
            },  # 13
            {
                "CHILD": "6666",
                "DECOM": "15/06/2020",
                "DEC": "16/06/2020",
                "REC": "X1",
            },  # 14  Fails Case 3
            {
                "CHILD": "77777",
                "DECOM": "16/06/2020",
                "DEC": "17/06/2020",
                "REC": "X1",
            },  # 15
            {
                "CHILD": "77777",
                "DECOM": "17/06/2020",
                "DEC": "18/06/2020",
                "REC": "X1",
            },  # 16
            {"CHILD": "77777", "DECOM": "18/06/2020", "DEC": pd.NA, "REC": pd.NA},  # 17
            {
                "CHILD": "999",
                "DECOM": "31/06/2020",
                "DEC": pd.NA,
                "REC": pd.NA,
            },  # 18   Nonsense date, but should pass
            {
                "CHILD": "123",
                "DECOM": pd.NA,
                "DEC": pd.NA,
                "REC": pd.NA,
            },  # 19   Nonsense dates, but should pass
            {
                "CHILD": pd.NA,
                "DECOM": pd.NA,
                "DEC": pd.NA,
                "REC": pd.NA,
            },  # 20   Nonsense, but should pass
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    

    result = validate(fake_dfs)

    assert result == {"Episodes": [0, 3, 5, 10, 14]}
