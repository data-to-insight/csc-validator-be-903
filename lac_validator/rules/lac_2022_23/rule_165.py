import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="165",
    message="Data entry for mother status is invalid.",
    affected_fields=["MOTHER", "SEX", "ACTIV", "ACCOM", "IN_TOUCH", "DECOM"],
)
def validate(dfs):
    if "Header" not in dfs or "Episodes" not in dfs or "OC3" not in dfs:
        return {}
    else:
        header = dfs["Header"]
        episodes = dfs["Episodes"]
        oc3 = dfs["OC3"]
        collection_start = dfs["metadata"]["collection_start"]
        collection_end = dfs["metadata"]["collection_end"]
        valid_values = ["0", "1"]

        # prepare to merge
        oc3.reset_index(inplace=True)
        header.reset_index(inplace=True)
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

        # Drop all episodes with V3/V4 legal status
        v3v4_ls = episodes["LS"].str.upper().isin(["V3", "V4"])
        index_v3v4_ls = episodes.loc[v3v4_ls].index
        episodes.drop(index_v3v4_ls, inplace=True)

        # fill in missing DECs with the collection year end date
        missing_last_DECs = episodes["DEC"].isna()
        episodes.loc[missing_last_DECs, "DEC"] = collection_end

        episodes["EPS"] = (episodes["DEC"] >= collection_start) & (
            episodes["DECOM"] <= collection_end
        )
        episodes["EPS_COUNT"] = episodes.groupby("CHILD")["EPS"].transform("sum")

        merged = episodes.merge(
            header, on="CHILD", how="left", suffixes=["_eps", "_er"]
        ).merge(oc3, on="CHILD", how="left")

        # Raise error if provided <MOTHER> is not a valid value
        value_validity = merged["MOTHER"].notna() & (
            ~merged["MOTHER"].astype(str).isin(valid_values)
        )

        # Raise error if provided <MOTHER> and child is male
        male = merged["MOTHER"].notna() & (merged["SEX"].astype(str) == "1")

        # Raise error if female and not provided
        female = merged["SEX"].astype(str) == "2"
        has_mother = merged["MOTHER"].notna()
        eps_in_year = merged["EPS_COUNT"] > 0
        has_oc3 = (
            merged["ACTIV"].notna()
            | merged["ACCOM"].notna()
            | merged["IN_TOUCH"].notna()
        )

        # If provided <MOTHER> must be a valid value (and child must be female). If not provided <MOTHER> then either <GENDER> is male or no episode record for current year and any of <IN_TOUCH>, <ACTIV> or <ACCOM> have been provided
        mask = (
            value_validity
            | male
            | (~has_mother & female & eps_in_year)
            | (has_mother & female & ~eps_in_year & has_oc3)
        )

        # That is, if value not provided and child is a female with eps in current year or no values of IN_TOUCH, ACTIV and ACCOM, then raise error.
        error_locs_eps = merged.loc[mask, "index_eps"]
        error_locs_header = merged.loc[mask, "index_er"]
        error_locs_oc3 = merged.loc[mask, "index"]

        return {
            "Header": error_locs_header.dropna().unique().tolist(),
            "OC3": error_locs_oc3.dropna().unique().tolist(),
        }


def test_validate():
    import pandas as pd

    fake_data_oc3 = pd.DataFrame(
        {
            "CHILD": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
            "IN_TOUCH": [
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                "YES",
                pd.NA,
                pd.NA,
                pd.NA,
            ],
            "ACTIV": [
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                "XXX",
                pd.NA,
                pd.NA,
                pd.NA,
            ],
            "ACCOM": [
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
                pd.NA,
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
            {"CHILD": 101, "DECOM": "01/01/2020", "DEC": "01/05/2020", "LS": "C2"},  # 0
            {"CHILD": 102, "DECOM": "11/01/2020", "DEC": "11/05/2020", "LS": "C2"},  # 1
            {"CHILD": 103, "DECOM": "30/03/2020", "DEC": "30/05/2020", "LS": "C2"},  # 2
            {"CHILD": 103, "DECOM": "30/03/2020", "DEC": "30/05/2020", "LS": "C2"},  # 2
            {"CHILD": 104, "DECOM": "01/01/2020", "DEC": "01/05/2020", "LS": "C2"},  # 3
            {"CHILD": 105, "DECOM": "11/05/2020", "DEC": "11/08/2020", "LS": "C2"},  # 4
            {"CHILD": 105, "DECOM": "01/01/2020", "DEC": "01/05/2020", "LS": "C2"},  # 5
            {"CHILD": 106, "DECOM": "22/01/2020", "DEC": "22/05/2020", "LS": "C2"},  # 6
            {"CHILD": 107, "DECOM": "11/01/2020", "DEC": "11/05/2020", "LS": "C2"},  # 7
            {"CHILD": 108, "DECOM": "22/01/2020", "DEC": "22/05/2020", "LS": "C2"},  # 8
            {"CHILD": 109, "DECOM": "25/03/2020", "DEC": "25/03/2020", "LS": "C2"},  # 9
            {
                "CHILD": 110,
                "DECOM": "01/01/2020",
                "DEC": "01/05/2020",
                "LS": "V3",
            },  # 10
            {
                "CHILD": 110,
                "DECOM": "01/11/2021",
                "DEC": "01/11/2021",
                "LS": "C2",
            },  # 11
            {
                "CHILD": 111,
                "DECOM": "01/11/2020",
                "DEC": "01/11/2020",
                "LS": "V3",
            },  # 12
        ]
    )
    fake_data_header = pd.DataFrame(
        [
            {"CHILD": 101, "SEX": "1", "MOTHER": pd.NA},  # 0 pass: male no value
            {"CHILD": 102, "SEX": "2", "MOTHER": "0"},  # 1 pass
            {"CHILD": 103, "SEX": "2", "MOTHER": 0},  # 2 pass
            {"CHILD": 104, "SEX": "2", "MOTHER": 1},  # 3 pass
            {"CHILD": 105, "SEX": "2", "MOTHER": pd.NA},  # 4 fail: no value
            {"CHILD": 106, "SEX": "2", "MOTHER": "2"},  # 5 fail: invalid value
            {"CHILD": 107, "SEX": "1", "MOTHER": "1"},  # 6 fail: male value
            {
                "CHILD": 108,
                "SEX": "2",
                "MOTHER": pd.NA,
            },  # 7 fail: has OC3 data but also has episode in collection year
            {
                "CHILD": 109,
                "SEX": "2",
                "MOTHER": pd.NA,
            },  # 8 pass: has OC3 and no episode in collection year
            {"CHILD": 110, "SEX": "2", "MOTHER": 1},
            # 9 pass: no non-V3/V4 episode in collection year and no OC3
            {"CHILD": 111, "SEX": "2", "MOTHER": pd.NA},  # 10 pass: V3 episode
        ]
    )
    metadata = {"collection_start": "01/04/2020", "collection_end": "31/03/2021"}
    fake_dfs = {
        "Header": fake_data_header,
        "Episodes": fake_data_episodes,
        "OC3": fake_data_oc3,
        "metadata": metadata,
    }
    error_defn, error_func = validate()
    result = error_func(fake_dfs)

    assert result == {"Header": [4, 5, 6, 7], "OC3": [4, 5, 6, 7]}
