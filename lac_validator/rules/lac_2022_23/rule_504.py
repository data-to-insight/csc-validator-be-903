import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="504",
    message="The category of need code differs from that reported at start of current period of being looked after",
    affected_fields=["CIN"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    else:
        epi = dfs["Episodes"]
        epi["DECOM"] = pd.todatetime(epi["DECOM"], format="%d/%m/%Y", errors="coerce")
        epi["DEC"] = pd.todatetime(epi["DEC"], format="%d/%m/%Y", errors="coerce")

        epi.sortvalues(["CHILD", "DECOM"], inplace=True)
        epi.resetindex(inplace=True)
        epi.resetindex(inplace=True)
        epi["LAGINDEX"] = epi["level0"].shift(1)

        mergeepi = epi.merge(
            epi,
            how="inner",
            lefton="LAGINDEX",
            righton="level0",
            suffixes=["", "PRE"],
        )
        mergeepi = mergeepi[mergeepi["CHILD"] == mergeepi["CHILDPRE"]]
        mergeepi = mergeepi[
            (mergeepi["RECPRE"] == "X1") & (mergeepi["DECPRE"] == mergeepi["DECOM"])
        ]
        errorcohort = mergeepi[mergeepi["CIN"] != mergeepi["CINPRE"]]
        errorlist = errorcohort["index"].unique().tolist()
        errorlist.sort()
        return {"Episodes": errorlist}


def test_validate():
    import pandas as pd

    fake_data = pd.DataFrame(
        [
            {
                "CHILD": "111",
                "DECOM": "01/06/2020",
                "DEC": "04/06/2020",
                "REC": "X1",
                "CIN": "N1",
            },  # 0
            {
                "CHILD": "111",
                "DECOM": "04/06/2020",
                "DEC": "06/06/2020",
                "REC": "X1",
                "CIN": "N2",
            },  # 1   Fails
            {
                "CHILD": "111",
                "DECOM": "06/06/2020",
                "DEC": pd.NA,
                "REC": "X1",
                "CIN": "N3",
            },  # 2   Fails
            {
                "CHILD": "111",
                "DECOM": "08/06/2020",
                "DEC": "09/06/2020",
                "REC": "X1",
                "CIN": "N2",
            },  # 3
            {
                "CHILD": "222",
                "DECOM": "10/06/2020",
                "DEC": "11/06/2020",
                "REC": "X1",
                "CIN": "N3",
            },  # 4
            {
                "CHILD": "333",
                "DECOM": "04/06/2020",
                "DEC": "07/06/2020",
                "REC": "X1",
                "CIN": "N4",
            },  # 5
            {
                "CHILD": "333",
                "DECOM": "07/06/2020",
                "DEC": pd.NA,
                "REC": "X1",
                "CIN": "N1",
            },  # 6   Fails
            {
                "CHILD": "444",
                "DECOM": "08/06/2020",
                "DEC": "09/06/2020",
                "REC": "X1",
                "CIN": "N2",
            },  # 7
            {
                "CHILD": "444",
                "DECOM": "08/06/2020",
                "DEC": "10/06/2020",
                "REC": "X1",
                "CIN": "N3",
            },  # 8
            {
                "CHILD": "444",
                "DECOM": "10/06/2020",
                "DEC": pd.NA,
                "REC": "X1",
                "CIN": "N4",
            },  # 9   Fails
        ]
    )

    fake_dfs = {"Episodes": fake_data}

    error_defn, error_func = validate()

    result = error_func(fake_dfs)

    assert result == {"Episodes": [1, 2, 6, 9]}
