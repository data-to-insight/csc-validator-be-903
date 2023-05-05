import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="225",
    message="Reason for placement change must be recorded.",
    affected_fields=["REASON_PLACE_CHANGE"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        epi["DECOM"] = pd.todatetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        epi.sortvalues(["CHILD", "DECOM"], inplace=True)
        epi.resetindex(inplace=True)
        epi.resetindex(inplace=True)
        epi["LAGINDEX"] = epi["level0"].shift(1)
        mepi = epi.merge(
            epi,
            how="inner",
            lefton="level0",
            righton="LAGINDEX",
            suffixes=["", "NEXT"],
        )
        mepi = mepi[mepi["CHILD"] == mepi["CHILDNEXT"]]

        maskisX1 = mepi["REC"] == "X1"
        masknullplacechg = mepi["REASONPLACECHANGE"].isna()
        maskplacenotT = ~mepi["PLACE"].isin(["T0", "T1", "T2", "T3", "T4"])
        masknextisPBTU = mepi["RNENEXT"].isin(["P", "B", "T", "U"])
        masknextplacenotT = ~mepi["PLACENEXT"].isin(["T0", "T1", "T2", "T3", "T4"])

        errormask = (
            maskisX1
            & masknullplacechg
            & maskplacenotT
            & masknextisPBTU
            & masknextplacenotT
        )

        errorlist = mepi["index"][errormask].tolist()
        return {"Episodes": errorlist}


def test_validate():
    import pandas as pd

    fake_data_epi = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DECOM": "01/06/2020",
                "RNE": "P",
                "REC": "X1",
                "PLACE": "U1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 0 Fails
            {
                "CHILD": "111",
                "DECOM": "05/06/2020",
                "RNE": "P",
                "REC": "E11",
                "PLACE": "X1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 1
            {
                "CHILD": "111",
                "DECOM": "06/06/2020",
                "RNE": "B",
                "REC": "E3",
                "PLACE": "X1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 2
            {
                "CHILD": "123",
                "DECOM": "08/06/2020",
                "RNE": "P",
                "REC": "X1",
                "PLACE": "U1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 3 Fails
            {
                "CHILD": "123",
                "DECOM": "10/06/2020",
                "RNE": "P",
                "REC": "E3",
                "PLACE": "X1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 4
            {
                "CHILD": "333",
                "DECOM": "06/06/2020",
                "RNE": "T",
                "REC": "X1",
                "PLACE": "U1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 5
            {
                "CHILD": "333",
                "DECOM": "07/06/2020",
                "RNE": "L",
                "REC": "X1",
                "PLACE": "X1",
                "REASON_PLACE_CHANGE": "CHANGE",
            },  # 6 Passes as RPC not null
            {
                "CHILD": "333",
                "DECOM": "08/06/2020",
                "RNE": "P",
                "REC": "E3",
                "PLACE": "U1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 7
            {
                "CHILD": "444",
                "DECOM": "09/06/2020",
                "RNE": "U",
                "REC": "X1",
                "PLACE": "T1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 8
            {
                "CHILD": "444",
                "DECOM": "15/06/2020",
                "RNE": "P",
                "REC": "X1",
                "PLACE": "X1",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 9 Passes next place T3
            {
                "CHILD": "444",
                "DECOM": "16/06/2020",
                "RNE": "P",
                "REC": "E3",
                "PLACE": "T3",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 10
            {
                "CHILD": "666",
                "DECOM": "17/06/2020",
                "RNE": "P",
                "REC": pd.NA,
                "PLACE": "T4",
                "REASON_PLACE_CHANGE": pd.NA,
            },  # 11
        ]
    )

    fake_dfs = {"Episodes": fake_data_epi}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [0, 3]}
