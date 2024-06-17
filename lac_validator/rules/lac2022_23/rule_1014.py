import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="1014",
    message="UASC information is not required for care leavers",
    affected_fields=["ACTIV", "ACCOM", "IN_TOUCH", "DUC"],
    tables=["Episodes", "UASC", "OC3"],
)
def validate(dfs):
    if "UASC" not in dfs or "Episodes" not in dfs or "OC3" not in dfs:
        return {}
    else:
        uasc = dfs["UASC"]
        episodes = dfs["Episodes"]
        oc3 = dfs["OC3"]
        collection_start = dfs["metadata"]["collection_start"]
        collection_end = dfs["metadata"]["collection_end"]

        # prepare to merge
        oc3.reset_index(inplace=True)
        uasc.reset_index(inplace=True)
        episodes.reset_index(inplace=True)

        collection_start = pd.to_datetime(
            collection_start, format="%d/%m/%Y", errors="coerce"
        )
        collection_end = pd.to_datetime(
            collection_end, format="%d/%m/%Y", errors="coerce"
        )
        episodes["DECOM"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        episodes["DEC"] = pd.to_datetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )

        date_check = (
            (episodes["DEC"] >= collection_start)
            & (episodes["DECOM"] <= collection_end)
        ) | ((episodes["DECOM"] <= collection_end) & episodes["DEC"].isna())
        episodes["EPS"] = date_check
        episodes["EPS_COUNT"] = episodes.groupby("CHILD")["EPS"].transform("sum")

        # inner merge to take only episodes of children which are also found on the uasc table
        merged = episodes.merge(
            uasc, on="CHILD", how="inner", suffixes=["_eps", "_sc"]
        ).merge(oc3, on="CHILD", how="left")
        # adding suffixes with the secondary merge here does not go so well yet.

        some_provided = (
            merged["ACTIV"].notna()
            | merged["ACCOM"].notna()
            | merged["IN_TOUCH"].notna()
        )

        mask = (merged["EPS_COUNT"] == 0) & some_provided

        error_locs_uasc = merged.loc[mask, "index_sc"]
        error_locs_oc3 = merged.loc[mask, "index"]

        return {
            "UASC": error_locs_uasc.unique().tolist(),
            "OC3": error_locs_oc3.unique().tolist(),
        }


def test_validate():
    import pandas as pd

    fake_data_uasc = pd.DataFrame(
        [
            {"CHILD": 101, "DOB": "01/06/2000", "DUC": "05/06/2019"},  # 0
            {"CHILD": 102, "DOB": "02/06/2000", "DUC": pd.NA},  # 1
            {"CHILD": 105, "DOB": "03/06/2000", "DUC": "01/06/2015"},  # 2
            {"CHILD": 107, "DOB": "04/06/2000", "DUC": "02/06/2020"},  # 3
            {"CHILD": 110, "DOB": pd.NA, "DUC": "05/06/2020"},  # 4 Fails
            {"CHILD": 111, "DOB": pd.NA, "DUC": "05/06/2020"},  # 5 Fails
        ]
    )
    fake_data_oc3 = pd.DataFrame(
        {
            "CHILD": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
            "IN_TOUCH": [
                pd.NA,
                "YES",
                "YES",
                pd.NA,
                "Yes",
                "No",
                "YES",
                "YES",
                pd.NA,
                pd.NA,
                "!!",
            ],
            "ACTIV": [
                pd.NA,
                pd.NA,
                "XXX",
                pd.NA,
                "XXX",
                pd.NA,
                pd.NA,
                "XXX",
                pd.NA,
                "XXX",
                "!!",
            ],
            "ACCOM": [
                pd.NA,
                pd.NA,
                pd.NA,
                "XXX",
                "XXX",
                pd.NA,
                pd.NA,
                pd.NA,
                "XXX",
                pd.NA,
                pd.NA,
            ],
        }
    )
    fake_data_episodes = pd.DataFrame(
        [
            {
                "CHILD": 101,
                "DECOM": "01/01/2020",
                "DEC": "01/01/2020",
            },  # 0
            {
                "CHILD": 102,
                "DECOM": "11/01/2020",
                "DEC": "11/01/2020",
            },  # 1
            {
                "CHILD": 103,
                "DECOM": "30/03/2020",
                "DEC": "30/03/2020",
            },  # 2
            {
                "CHILD": 104,
                "DECOM": "01/01/2020",
                "DEC": "01/01/2020",
            },  # 3
            {
                "CHILD": 105,
                "DECOM": "11/05/2020",
                "DEC": "11/05/2020",
            },  # 4 eps in range
            {
                "CHILD": 105,
                "DECOM": "01/01/2020",
                "DEC": "01/01/2020",
            },  # 5
            {
                "CHILD": 106,
                "DECOM": "22/01/2020",
                "DEC": "22/01/2020",
            },  # 6
            {
                "CHILD": 107,
                "DECOM": "11/01/2020",
                "DEC": "11/01/2020",
            },  # 7
            {
                "CHILD": 108,
                "DECOM": "22/01/2020",
                "DEC": "22/01/2020",
            },  # 8
            {
                "CHILD": 109,
                "DECOM": "25/03/2020",
                "DEC": "25/03/2020",
            },  # 9
            {
                "CHILD": 110,
                "DECOM": "01/01/2020",
                "DEC": "01/01/2020",
            },  # 10 fail.
            {
                "CHILD": 110,
                "DECOM": "01/11/2021",
                "DEC": "01/11/2021",
            },  # 11
            {
                "CHILD": 111,
                "DECOM": "01/11/2019",
                "DEC": "31/03/2021",
            },  # 12
        ]
    )

    metadata = {"collection_start": "01/04/2020", "collection_end": "31/03/2021"}
    fake_dfs = {
        "UASC": fake_data_uasc,
        "Episodes": fake_data_episodes,
        "OC3": fake_data_oc3,
        "metadata": metadata,
    }

    result = validate(fake_dfs)
    # assert result == {'UASC': [2], 'Episodes': [4,5], 'OC3':[4]}
    assert result == {"UASC": [1, 3, 4], "OC3": [1, 6, 9]}
