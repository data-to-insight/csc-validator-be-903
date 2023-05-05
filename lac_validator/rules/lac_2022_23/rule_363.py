import pandas as pd

from validator903.types import ErrorDefinition


@rule_definition(
    code="363",
    message="Child assessment order (CAO) lasted longer than 7 days allowed in the Children Act 1989.",
    affected_fields=["LS", "DECOM", "DEC"],
)
def validate(dfs):
    if "Episodes" not in dfs:
        return {}
    episodes = dfs["Episodes"]
    collectionendstr = dfs["metadata"]["collectionend"]

    L2eps = episodes[episodes["LS"] == "L3"].copy()
    L2eps["originalindex"] = L2eps.index
    L2eps = L2eps[L2eps["DECOM"].notna()]

    L2eps.loc[L2eps["DEC"].isna(), "DEC"] = collectionendstr
    L2eps["DECOM"] = pd.todatetime(L2eps["DECOM"], format="%d/%m/%Y", errors="coerce")
    L2eps = L2eps.dropna(subset=["DECOM"])
    L2eps["DEC"] = pd.todatetime(L2eps["DEC"], format="%d/%m/%Y", errors="coerce")

    L2eps.sortvalues(["CHILD", "DECOM"])

    L2eps["index"] = pd.RangeIndex(0, len(L2eps))
    L2eps["index+1"] = L2eps["index"] + 1
    L2eps = L2eps.merge(
        L2eps,
        lefton="index",
        righton="index+1",
        how="left",
        suffixes=[None, "prev"],
    )
    L2eps = L2eps[
        ["originalindex", "DECOM", "DEC", "DECprev", "CHILD", "CHILDprev", "LS"]
    ]

    L2eps["newperiod"] = (L2eps["DECOM"] > L2eps["DECprev"]) | (
        L2eps["CHILD"] != L2eps["CHILDprev"]
    )

    L2eps["duration"] = (L2eps["DEC"] - L2eps["DECOM"]).dt.days
    L2eps["periodid"] = L2eps["newperiod"].astype(int).cumsum()
    L2eps["periodduration"] = L2eps.groupby("periodid")["duration"].transform(sum)

    errormask = L2eps["periodduration"] > 7

    return {"Episodes": L2eps.loc[errormask, "originalindex"].tolist()}


def test_validate():
    import pandas as pd

    test_eps = pd.DataFrame(
        [
            {
                "CHILD": 101,
                "DECOM": "01/01/2000",
                "DEC": "01/01/2001",
                "LS": "L3",
            },  # 0 Fail!
            {"CHILD": 101, "DECOM": "01/01/2001", "DEC": "20/12/2001", "LS": "X"},  # 1
            {
                "CHILD": 101,
                "DECOM": "20/12/2001",
                "DEC": "12/01/2002",
                "LS": "L3",
            },  # 2 Fail!
            {
                "CHILD": 2002,
                "DECOM": "01/01/2000",
                "DEC": "03/01/2000",
                "LS": "L3",
            },  # 3 ^ Fa
            {
                "CHILD": 2002,
                "DECOM": "03/01/2000",
                "DEC": "09/01/2001",
                "LS": "L3",
            },  # 4 v il!
            {
                "CHILD": 2002,
                "DECOM": "01/01/2002",
                "DEC": "07/01/2002",
                "LS": "L3",
            },  # 5
            {"CHILD": 2002, "DECOM": "10/01/2002", "DEC": "11/01/2002", "LS": "X"},  # 6
            {
                "CHILD": 2002,
                "DECOM": "11/01/2002",
                "DEC": "17/01/2002",
                "LS": "L3",
            },  # 7
            {
                "CHILD": 30003,
                "DECOM": "25/01/2002",
                "DEC": "10/03/2001",
                "LS": "L3",
            },  # 8 (decom>dec)
            {
                "CHILD": 30003,
                "DECOM": "25/01/2002",
                "DEC": pd.NA,
                "LS": "L3",
            },  # 9 Fail!
            {
                "CHILD": 30003,
                "DECOM": pd.NA,
                "DEC": "25/01/2002",
                "LS": "L3",
            },  # 10 decom.isNA
            {"CHILD": 30003, "DECOM": pd.NA, "DEC": pd.NA, "LS": "L3"},  # 11
        ]
    )

    test_meta = {"collection_end": "01/04/2002"}

    test_dfs = {"Episodes": test_eps, "metadata": test_meta}

    error_defn, error_func = validate()

    result = error_func(test_dfs)

    assert result == {"Episodes": [0, 2, 3, 4, 9]}
