import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="433",
    message="The reason for new episode suggests that this is a continuation episode, but the episode does not start on the same day as the last episode finished.",
    affected_fields=["RNE", "DECOM"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]
        episodes["DECOM_dt"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )
        episodes["DEC_dt"] = pd.to_datetime(
            episodes["DEC"], format="%d/%m/%Y", errors="coerce"
        )

        episodes["original_index"] = episodes.index
        episodes.sort_values(["CHILD", "DECOM_dt", "DEC_dt"], inplace=True)
        episodes[["PREVIOUS_DEC", "PREVIOUS_CHILD"]] = episodes[["DEC", "CHILD"]].shift(
            1
        )

        rne_is_ongoing = (
            episodes["RNE"].str.upper().astype(str).isin(["P", "L", "T", "U", "B"])
        )
        date_mismatch = episodes["PREVIOUS_DEC"] != episodes["DECOM"]
        missing_date = episodes["PREVIOUS_DEC"].isna() | episodes["DECOM"].isna()
        same_child = episodes["PREVIOUS_CHILD"] == episodes["CHILD"]

        error_mask = rne_is_ongoing & (date_mismatch | missing_date) & same_child

        error_locations = episodes["original_index"].loc[error_mask].sort_values()

        return {"Episodes": error_locations.to_list()}


def test_validate():
    import pandas as pd

    fake_data_episodes = pd.DataFrame(
        [
            {
                "CHILD": "101",
                "DECOM": "20/10/2021",
                "RNE": "S",
                "DEC": "20/11/2021",
            },  # 0: Ignore
            {
                "CHILD": "102",
                "DECOM": "19/11/2021",
                "RNE": "P",
                "DEC": pd.NA,
            },  # 1 [102:2nd]
            {
                "CHILD": "102",
                "DECOM": "17/06/2021",
                "RNE": "P",
                "DEC": "19/11/2021",
            },  # 2 [102:1st]
            {
                "CHILD": "103",
                "DECOM": "04/04/2020",
                "RNE": "B",
                "DEC": "12/09/2020",
            },  # 3 [103:1st]
            {
                "CHILD": "103",
                "DECOM": "11/09/2020",
                "RNE": "B",
                "DEC": "06/05/2021",
            },  # 4 [103:2nd] ]Fail!
            {
                "CHILD": "103",
                "DECOM": "07/05/2021",
                "RNE": "B",
                "DEC": pd.NA,
            },  # 5 [103:3rd] Fail!
        ]
    )

    fake_dfs = {"Episodes": fake_data_episodes}

    

    result = validate(fake_dfs)

    assert result == {"Episodes": [4, 5]}
