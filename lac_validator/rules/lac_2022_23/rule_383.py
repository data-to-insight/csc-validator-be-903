import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="383",
    message="A child in a temporary placement must subsequently return to his/her normal placement.",
    affected_fields=["PLACE"],
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
        epi["LAGINDEX"] = epi["level0"].shift(-1)
        epi["LEADINDEX"] = epi["level0"].shift(1)

        mepi = epi.merge(
            epi,
            how="inner",
            lefton="level0",
            righton="LAGINDEX",
            suffixes=["", "TOP"],
        )
        mepi = mepi.merge(
            epi,
            how="inner",
            lefton="level0",
            righton="LEADINDEX",
            suffixes=["", "BOTM"],
        )
        mepi = mepi[mepi["CHILD"] == mepi["CHILDTOP"]]
        mepi = mepi[mepi["CHILD"] == mepi["CHILDBOTM"]]
        mepi = mepi[mepi["PLACE"].isin(["T0", "T1", "T2", "T3", "T4"])]

        mask1 = mepi["RNEBOTM"] != "P"
        mask2 = mepi["PLACEBOTM"] != mepi["PLACETOP"]
        errmask = mask1 | mask2
        errlist = mepi["index"][errmask].unique().tolist()
        errlist.sort()
        return {"Episodes": errlist}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {"CHILD": "111", "RNE": "S", "DECOM": "01/06/2020", "PLACE": "S1"},  # 0
            {
                "CHILD": "111",
                "RNE": "S",
                "DECOM": "05/06/2020",
                "PLACE": "T1",
            },  # 1 Middle Fails as next RNE not P
            {"CHILD": "111", "RNE": "T", "DECOM": "06/06/2020", "PLACE": "S1"},  # 2
            {"CHILD": "222", "RNE": "S", "DECOM": "05/06/2020", "PLACE": "T1"},  # 3
            {"CHILD": "333", "RNE": "S", "DECOM": "06/06/2020", "PLACE": "S1"},  # 4
            {
                "CHILD": "333",
                "RNE": "S",
                "DECOM": "10/06/2020",
                "PLACE": "T1",
            },  # 5 Middle Fails as pre PL not next PL
            {"CHILD": "333", "RNE": "P", "DECOM": "12/06/2020", "PLACE": "S2"},  # 6
            {"CHILD": "444", "RNE": "S", "DECOM": "08/06/2020", "PLACE": "T1"},  # 7
            {
                "CHILD": "444",
                "RNE": "S",
                "DECOM": "09/06/2020",
                "PLACE": "P4",
            },  # 8  Middle Passes not a T code
            {"CHILD": "444", "RNE": "S", "DECOM": "15/06/2020", "PLACE": "T1"},  # 9
            {"CHILD": "6666", "RNE": "S", "DECOM": "12/06/2020", "PLACE": "T1"},  # 10
            {
                "CHILD": "6666",
                "RNE": "S",
                "DECOM": "13/06/2020",
                "PLACE": "T1",
            },  # 11 Middle Passes
            {"CHILD": "6666", "RNE": "P", "DECOM": "14/06/2020", "PLACE": "T1"},  # 12
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1, 5]}
