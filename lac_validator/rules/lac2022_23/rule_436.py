import pandas as pd

from lac_validator.rule_engine import rule_definition


import pandas as pd


@rule_definition(
    code="436",
    message="Reason for new episode is that both child’s placement and legal status have changed, but this is not reflected in the episode data.",
    affected_fields=["RNE", "LS", "PLACE", "PL_POST", "URN", "PLACE_PROVIDER"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        epi["DECOM"] = pd.to_datetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")

        epi.sort_values(["CHILD", "DECOM"], inplace=True)
        epi.reset_index(inplace=True)
        epi.reset_index(inplace=True)
        epi["LAG_INDEX"] = epi["level_0"].shift(-1)
        epi.fillna(
            value={
                "LS": "*",
                "PLACE": "*",
                "PL_POST": "*",
                "URN": "*",
                "PLACE_PROVIDER": "*",
            },
            inplace=True,
        )
        epi_merge = epi.merge(
            epi,
            how="inner",
            left_on="level_0",
            right_on="LAG_INDEX",
            suffixes=["", "_PRE"],
        )

        epi_multi_row = epi_merge[epi_merge["CHILD"] == epi_merge["CHILD_PRE"]]
        epi_has_B_U = epi_multi_row[epi_multi_row["RNE"].isin(["U", "B"])]

        mask_ls = epi_has_B_U["LS"] == epi_has_B_U["LS_PRE"]

        mask1 = epi_has_B_U["PLACE"] == epi_has_B_U["PLACE_PRE"]
        mask2 = epi_has_B_U["PL_POST"] == epi_has_B_U["PL_POST_PRE"]
        mask3 = epi_has_B_U["URN"] == epi_has_B_U["URN_PRE"]
        mask4 = epi_has_B_U["PLACE_PROVIDER"] == epi_has_B_U["PLACE_PROVIDER_PRE"]

        error_mask = mask_ls | (mask1 & mask2 & mask3 & mask4)

        error_list = epi_has_B_U[error_mask]["index"].to_list()
        error_list.sort()
        return {"Episodes": error_list}


def test_validate():
    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "11",
                "DECOM": "03/06/2020",
                "RNE": "P",
                "LS": "P",
                "PLACE": "X1",
                "PL_POST": "X1",
                "URN": "R",
                "PLACE_PROVIDER": "b",
            },  # 0
            {
                "CHILD": "11",
                "DECOM": "05/06/2020",
                "RNE": "U",
                "LS": "X",
                "PLACE": "X1",
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 1
            {
                "CHILD": "11",
                "DECOM": "06/06/2020",
                "RNE": "B",
                "LS": "P",
                "PLACE": "X1",
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 2 Fails diff LS, same PLACE et. al
            {
                "CHILD": "11",
                "DECOM": "08/06/2020",
                "RNE": "U",
                "LS": "X",
                "PLACE": "X1",
                "PL_POST": "TT",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 3
            {
                "CHILD": "22",
                "DECOM": "05/06/2020",
                "RNE": "U",
                "LS": "P",
                "PLACE": pd.NA,
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 4
            {
                "CHILD": "33",
                "DECOM": "06/06/2020",
                "RNE": "P",
                "LS": "P",
                "PLACE": "E11",
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 5
            {
                "CHILD": "33",
                "DECOM": "07/06/2020",
                "RNE": "B",
                "LS": pd.NA,
                "PLACE": pd.NA,
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 6
            {
                "CHILD": "44",
                "DECOM": "08/06/2020",
                "RNE": "T",
                "LS": "P",
                "PLACE": "X1",
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 7
            {
                "CHILD": "44",
                "DECOM": "09/06/2020",
                "RNE": "B",
                "LS": "P",
                "PLACE": "E11",
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 8 Fails same LS
            {
                "CHILD": "44",
                "DECOM": "15/06/2020",
                "RNE": "B",
                "LS": "P",
                "PLACE": pd.NA,
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 9 Fails same LS
            {
                "CHILD": "55",
                "DECOM": "11/06/2020",
                "RNE": "P",
                "LS": "P",
                "PLACE": "X1",
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 10
            {
                "CHILD": "66",
                "DECOM": "12/06/2020",
                "RNE": "P",
                "LS": "P",
                "PLACE": "X1",
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 11
            {
                "CHILD": "66",
                "DECOM": "13/06/2020",
                "RNE": "P",
                "LS": "P",
                "PLACE": "X1",
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 12
            {
                "CHILD": "66",
                "DECOM": "14/06/2020",
                "RNE": "B",
                "LS": "X",
                "PLACE": "X1",
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 13 Fails diff LS, same PLACE et. al
            {
                "CHILD": "66",
                "DECOM": "15/06/2020",
                "RNE": "P",
                "LS": "P",
                "PLACE": "X1",
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 14
            {
                "CHILD": "77",
                "DECOM": "16/06/2020",
                "RNE": "P",
                "LS": "P",
                "PLACE": "X1",
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 15
            {
                "CHILD": "77",
                "DECOM": "17/06/2020",
                "RNE": "B",
                "LS": "P",
                "PLACE": "X1",
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 16  Fails same PLACE et. al
            {
                "CHILD": "77",
                "DECOM": "18/06/2020",
                "RNE": "P",
                "LS": pd.NA,
                "PLACE": pd.NA,
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 17
            {
                "CHILD": "99",
                "DECOM": "31/06/2020",
                "RNE": "P",
                "LS": pd.NA,
                "PLACE": pd.NA,
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 18
            {
                "CHILD": "12",
                "DECOM": pd.NA,
                "RNE": "U",
                "LS": pd.NA,
                "PLACE": pd.NA,
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 19
            {
                "CHILD": pd.NA,
                "DECOM": pd.NA,
                "RNE": "U",
                "LS": pd.NA,
                "PLACE": pd.NA,
                "PL_POST": "X1",
                "URN": "a",
                "PLACE_PROVIDER": "b",
            },  # 20
        ]
    )

    fake_dfs = {"Episodes": fake_data}
    result = validate(fake_dfs)
    assert result == {"Episodes": [2, 8, 9, 13, 16]}
