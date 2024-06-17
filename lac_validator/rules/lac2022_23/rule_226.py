import pandas as pd

from lac_validator.rule_engine import rule_definition


@rule_definition(
    code="226",
    message="Reason for placement change is not required.",
    affected_fields=["REASON_PLACE_CHANGE", "PLACE"],
    tables=["Episodes"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        episodes = dfs["Episodes"]

        code_list = ["T0", "T1", "T2", "T3", "T4"]

        episodes["DECOM"] = pd.to_datetime(
            episodes["DECOM"], format="%d/%m/%Y", errors="coerce"
        )

        # create column to see previous REASON_PLACE_CHANGE
        episodes = episodes.sort_values(["CHILD", "DECOM"])
        episodes["PREVIOUS_REASON"] = episodes.groupby("CHILD")[
            "REASON_PLACE_CHANGE"
        ].shift(1)
        # If <PL> = 'T0'; 'T1'; 'T2'; 'T3' or 'T4' then <REASON_PLACE_CHANGE> should be null in current episode and current episode - 1
        mask = episodes["PLACE"].isin(code_list) & (
            episodes["REASON_PLACE_CHANGE"].notna()
            | episodes["PREVIOUS_REASON"].notna()
        )

        # error locations
        error_locs = episodes.index[mask]
    return {"Episodes": error_locs.tolist()}


def test_validate():
    import pandas as pd

    fake_data_epi = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DECOM": "01/01/2020",
                "PLACE": "U1",
                "REASON_PLACE_CHANGE": "XXX",
            },  # 0
            {
                "CHILD": "111",
                "DECOM": "11/01/2020",
                "PLACE": "T1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 1 Fail
            {
                "CHILD": "111",
                "DECOM": "22/01/2020",
                "PLACE": "X1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 2
            {
                "CHILD": "123",
                "DECOM": "01/01/2020",
                "PLACE": "U1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 3
            {
                "CHILD": "123",
                "DECOM": "11/01/2020",
                "PLACE": "X1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 4
            {
                "CHILD": "333",
                "DECOM": "01/01/2020",
                "PLACE": "T2",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 5
            {
                "CHILD": "333",
                "DECOM": "22/01/2020",
                "PLACE": "X1",
                "REASON_PLACE_CHANGE": "CHANGE",
            },  # 6
            {
                "CHILD": "333",
                "DECOM": "11/01/2020",
                "PLACE": "U1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 7
            {
                "CHILD": "444",
                "DECOM": "22/01/2020",
                "PLACE": "T1",
                "REASON_PLACE_CHANGE": "XXX",
            },  # 8 Fail
            {
                "CHILD": "444",
                "DECOM": "11/01/2020",
                "PLACE": "X1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 9
            {
                "CHILD": "444",
                "DECOM": "01/01/2020",
                "PLACE": "T3",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 10 Pass
            {
                "CHILD": "666",
                "DECOM": "01/01/2020",
                "PLACE": "T4",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 11 Pass
        ]
    )
    fake_dfs = {"Episodes": fake_data_epi}

    result = validate(fake_dfs)
    assert result == {"Episodes": [1, 8]}
